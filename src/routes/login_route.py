from quart import Blueprint, jsonify, request
from db import get_sqlalchemy_session
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberBannedError,
    PhoneNumberFloodError,
    PhoneNumberInvalidError,
    AuthRestartError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneCodeEmptyError,
)
from collections import defaultdict
from config import Config
from services.user_service import set_has_profile, set_auth_status, get_user_chats
from models import User, Chat, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from utils import get_chat_id, count_words, connect_client, disconnect_client
from services.session_service import (
    create_sqlalchemy_session,
    fetch_user_session,
    delete_session,
    set_session_is_logged_and_user_id,
    set_session_chats,
)
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.types import User, Chat, Channel
import asyncio
import logging

logger = logging.getLogger(__name__)

login_route = Blueprint("login_route", __name__)


@login_route.route("/login", methods=["POST"])
async def login():
    data = await request.get_json()

    auth_code = data.get("code")
    password = data.get("password")
    if not auth_code and not password:
        return jsonify({"error": "No code provided"}), 400

    user_id = data.get("userId")
    phone_number = data.get("phone_number")
    if not phone_number and not user_id:
        return jsonify({"error": "No phone_number or user_id provided"}), 400

    print(f"{phone_number}({user_id}) is trying to login with: {auth_code}({password})")

    # user_db_session = await get_db_session(phone_number, user_id)
    user_db_session = await fetch_user_session(phone_number, user_id)
    if user_db_session is None:
        logger.error(f"{phone_number} session does not exist")
        return jsonify({"error": "session does not exist"}), 500

    client = TelegramClient(
        StringSession(user_db_session.id), Config.API_ID, Config.API_HASH
    )

    if await connect_client(client, phone_number, user_id) == -1:
        return jsonify({"error": "error in connecting to Telegram"}), 500

    if await client.is_user_authorized() == True:
        await disconnect_client(client, f"{phone_number} is already logged in")
        return jsonify({"message": "user is already logged in"}), 409

    try:
        if password is None:
            await client.sign_in(
                phone=user_db_session.phone_number,
                code=auth_code,
                phone_code_hash=user_db_session.phone_code_hash,
            )
        else:
            logger.info("Signing in with password")
            await client.sign_in(password=password)
    except SessionPasswordNeededError:
        await disconnect_client(client, "two-steps verification is active")
        return jsonify({"error": "two-steps verification is active"}), 401
    except PhoneCodeExpiredError:
        await disconnect_client(client, "The confirmation code has expired")
        return jsonify({"error": "The confirmation code has expired"}), 410
    except PhoneCodeInvalidError:
        await disconnect_client(client, "The auth code is invalid")
        return jsonify({"error": "The auth code is invalid"}), 403
    except PhoneNumberInvalidError:
        await disconnect_client(client, "The phone number is invalid")
        return jsonify({"error": "The phone number is invalid"}), 422
    except Exception as e:
        exception_type = type(e).__name__
        await disconnect_client(
            client, f"Error in sign_in(): {exception_type} - {str(e)}"
        )
        return jsonify({"error": f"{exception_type}: {str(e)}"}), 500

    logger.info(f"{phone_number} is logged in")

    sender = await client.get_me()

    await set_session_is_logged_and_user_id(phone_number, sender.id)

    chat_ids = await get_user_chats(sender.id, sender.username)
    if chat_ids == 1:
        await disconnect_client(client, "Error while retrieving user's chats")
        return jsonify({"message": "error while retrieving user's chats"}), 500

    status = await set_has_profile(sender.id, True)
    if status == 1:
        await disconnect_client(client, "Couldn't set has_profile to True")
        return jsonify({"error": "couldn't set has_profile to True"}), 500

    count = 0
    res = defaultdict(int)
    tasks = []

    try:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            entity = dialog.entity
            if not (
                isinstance(entity, Chat)
                or (isinstance(entity, User) and dialog.entity.bot == False)
            ):
                continue

            private_chat_id = await get_chat_id(dialog.id, sender.id, client)
            if private_chat_id in chat_ids:
                logger.info(f"Chat {dialog.name} is already sold")
                continue

            # TODO: think about the limit of chats
            count += 1
            if count > 15:
                break
            logger.info(f"{dialog.name}")
            task = asyncio.create_task(count_words(dialog.id, client))
            tasks.append((dialog.id, dialog.name, task))
    except Exception as e:
        await disconnect_client(client, f"Error in get_dialogs(): {str(e)}")
        return jsonify({"error": str(e)}), 500

    results = await asyncio.gather(*(task for _, _, task in tasks))
    for (dialog_id, dialog_name, _), word_count in zip(tasks, results):
        res[(dialog_id, dialog_name)] = word_count

    status = await set_auth_status(sender.id, "choose_chat")
    if status == 1:
        await disconnect_client(client, "couldn't update auth_status")
        return jsonify({"error": "couldn't update auth_status"}), 500

    res_json_serializable = {str(key): value for key, value in res.items()}

    await set_session_chats(phone_number, str(res_json_serializable))

    # Print the JSON-serializable dictionary
    logger.info(res_json_serializable)
    return jsonify(res_json_serializable), 200


@login_route.route("/send-code", methods=["POST"])
async def send_code():
    logger.info("send-code endpoint called")
    try:
        data = await request.get_json()
        logger.info(f"send-code: {data}")

        phone_number = data.get("phone_number")
        if phone_number is None:
            logger.error("phone_number is missing")
            return jsonify({"error": "phone_number is missing"}), 400

        user_id = data.get("userId")

        # TODO: check how long ago we send previous code
        client = None
        user_db_session = await fetch_user_session(phone_number, user_id)
        if user_db_session is None:
            logger.info(
                f"No existing session for {phone_number}, creating new Telegram client, i.e. session"
            )
            client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
        else:
            logger.info(
                f"Existing session found for {phone_number}, creating Telegram client with existing session"
            )
            client = TelegramClient(
                StringSession(user_db_session.id), Config.API_ID, Config.API_HASH
            )

        if await connect_client(client, phone_number, user_id) == -1:
            logger.error("Error in connecting to Telegram")
            return jsonify({"error": "error in connecting to Telegram"}), 500

        if await client.is_user_authorized() == True:
            await disconnect_client(client, f"{phone_number} is already logged in")
            logger.info(f"{phone_number} is already logged in")
            return jsonify({"message": "user is already logged in"}), 409

        try:
            result = await client.send_code_request(phone_number)
            phone_code_hash = result.phone_code_hash
            logger.info(f"Auth code sent to {phone_number}")
        except PhoneNumberBannedError as e:
            await disconnect_client(
                client, f"The used phone number has been banned from Telegram: {str(e)}"
            )
            logger.error(
                f"The used phone number has been banned from Telegram: {str(e)}"
            )
            await disconnect_client(
                client, f"The used phone number has been banned from Telegram: {str(e)}"
            )
            return jsonify({"error": str(e)}), 403

        except PhoneNumberFloodError as e:
            await disconnect_client(
                client, f"You asked for the code too many times: {str(e)}"
            )
            logger.error(f"You asked for the code too many times: {str(e)}")
            await disconnect_client(
                client, f"You asked for the code too many times: {str(e)}"
            )
            logger.error(f"You asked for the code too many times: {str(e)}")
            return jsonify({"error": str(e)}), 429

        except PhoneNumberInvalidError as e:
            await disconnect_client(client, f"phone number is invalid: {str(e)}")
            return jsonify({"error": str(e)}), 404

        except AuthRestartError as e:
            print(f"auth restart error: {str(e)}")
            await client.send_code_request(phone_number)

        except Exception as e:
            await disconnect_client(client, f"Error in send_code(): {str(e)}")
            logger.error(f"Error in send_code(): {str(e)}")
            return jsonify({"error": str(e)}), 500

        logger.info(f"sending auth code to {phone_number}")

        if user_db_session is None:
            status = await create_sqlalchemy_session(
                client, phone_number, phone_code_hash, user_id
            )
            if status == -1:
                await disconnect_client(client, "Error creating session")
                logger.error("Error creating session")
                return jsonify({"message": "error creating session"}), 500
            logger.info(f"Session created for {phone_number}")

        # TODO: We get this error if the userId is wrong but the phone number is correct
        if user_id is not None:
            status = await set_auth_status(user_id, "auth_code")
            if status == 1:
                await disconnect_client(client, "Couldn't update auth_status")
                logger.error("Couldn't update auth_status")
                return jsonify({"error": "couldn't update auth_status"}), 500
        logger.info("send-code: ok")
        return "ok", 200

    except Exception as e:
        logger.error(f"Error in send-code: {str(e)}")
        return jsonify({"error": str(e)}), 500
