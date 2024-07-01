from quart import Blueprint, jsonify, request
from db import Session
from telethon.errors import SessionPasswordNeededError, PhoneNumberBannedError, PhoneNumberFloodError, PhoneNumberInvalidError, AuthRestartError, PhoneCodeExpiredError, PhoneCodeInvalidError, PhoneCodeEmptyError
from collections import defaultdict
from client_wrapper import ClientWrapper
from config import Config
from services.user_service import set_has_profile, set_auth_status
from models import User, Chat, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from utils import get_chat_id, count_words, connect_client
from services.user_service import get_user_chats
from services.session_service import create_session, session_exists, delete_session
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import os

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

login_route = Blueprint('login_route', __name__)

@login_route.route('/login', methods=['POST'])
async def login():
    data = await request.get_json()

    auth_code = data.get("code")
    if not auth_code:
        return jsonify({"error": "No code provided"}), 400
    
    phone_number = data.get("phone_number")
    if not phone_number:
        return jsonify({"error": "No phone_number provided"}), 400
    
    print(f"{phone_number} is trying to login with: {auth_code}")

    saved_client = await session_exists(phone_number)
    
    if saved_client is None:
        print(f"{phone_number} session does not exist")
        return jsonify({"error": "session does not exist"}), 500
    
    client = TelegramClient(StringSession(saved_client.id), API_ID, API_HASH)

    if await connect_client(client, phone_number) == -1:
        return jsonify({"error": "error in connecting to Telegram"}), 500
    
    if await client.is_user_authorized() == True:
        print(f"{phone_number} is already logged in")
        return jsonify({"message": "user is already logged in"}), 409
    
    try:
        await client.sign_in(phone=phone_number, code=auth_code, phone_code_hash=saved_client.phone_code_hash)
    except SessionPasswordNeededError:
        print("two-steps verification is active")
        return jsonify({"error": "two-steps verification is active"}), 401
    except PhoneCodeExpiredError:
        print("The confirmation code has expired")
        return jsonify({"error": "The confirmation code has expired"}), 400
    except PhoneCodeInvalidError:
        print("The auth code entered was invalid")
        return jsonify({"error": "The auth code entered was invalid"}), 400
    except PhoneCodeEmptyError:
        print("The auth code is missing")
        return jsonify({"error": "The auth code is missing"}), 400
    except PhoneNumberInvalidError:
        print("The phone number entered was invalid")
        return jsonify({"error": "The phone number entered was invalid"}), 400
    except Exception as e:
        exception_type = type(e).__name__
        print(f"Error in sign_in(): {exception_type} - {str(e)}")
        return jsonify({"error": f"{exception_type}: {str(e)}"}), 500

    print(f"{phone_number} is logged in")

    sender = None

    if await client.is_user_authorized() == True:
        sender = await client.get_me()
    else:
        print(f"{phone_number} manually logged out")
        return jsonify({"message": "manually logged out"}), 500

    chat_ids = await get_user_chats(sender.id, sender.username)
    if chat_ids == 1:
        return jsonify({"message": "error while retrieving user's chats"}), 500
    
    # TODO: handle this error properly
    status = await set_has_profile(sender.id, True)
    if status == 1:
        return jsonify({"error": "couldn't set has_profile to True"}), 500
    
    count = 0
    res = defaultdict(int)

    try:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            if dialog.id < 0 or dialog.entity.bot == True or dialog.id == 777000:
                continue

            private_chat_id = await get_chat_id(dialog.id, sender.id, client)
            if private_chat_id in chat_ids:
                print(f"Chat {dialog.name} is already sold")
                continue
    
            # TODO: think about the limit of chats
            count += 1
            if count > 15:
                break

            print(f"{dialog.name}")
            word_count = await count_words(dialog.id, client)
            res[(dialog.id, dialog.name)] = word_count
    except Exception as e:
        print(f"Error in get_dialogs(): {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    # TODO: handle this error properly
    status = await set_auth_status(sender.id, "choose_chat")
    if status == 1:
        return jsonify({"error": "couldn't update auth_status"}), 500

    res_json_serializable = {str(key): value for key, value in res.items()}

    # Print the JSON-serializable dictionary
    print(res_json_serializable)
    return jsonify(res_json_serializable), 200


@login_route.route("/send-code", methods=["POST"])
async def send_code():
    try:
        data = await request.get_json()

        phone_number = data.get("phone_number")
        if phone_number is None:
            return jsonify({"error": "phone_number is missing"}), 400
        
        user_id = data.get("user_id")
        if user_id is None:
            print(f"{phone_number} entered from browser")
        
        # if session exists but not logged in => deletes the session
        # TODO: check how long ago we send previous code
        client = None
        saved_client = await session_exists(phone_number)
        
        if saved_client is None:
            client = TelegramClient(StringSession(), API_ID, API_HASH)
        
        if saved_client is not None:
            client = TelegramClient(StringSession(saved_client.id), API_ID, API_HASH)

        if await connect_client(client, phone_number) == -1:
            return jsonify({"error": "error in connecting to Telegram"}), 500
    
        if await client.is_user_authorized() == True:
            print(f"{phone_number} is already logged in")
            return jsonify({"message": "user is already logged in"}), 409
        
        try:
            result = await client.send_code_request(phone_number)
            phone_code_hash = result.phone_code_hash
        except PhoneNumberBannedError as e:
            print(f"The used phone number has been banned from Telegram: {str(e)}")
            return jsonify({"error": str(e)}), 403
        except PhoneNumberFloodError as e:
            print(f"You asked for the code too many times: {str(e)}")
            return jsonify({"error": str(e)}), 429
        except PhoneNumberInvalidError as e:
            print(f"phone number is invalid: {str(e)}")
            return jsonify({"error": str(e)}), 404
        except AuthRestartError as e:
            print(f"auth restart error: {str(e)}")
            await client.send_code_request(phone_number)
        except Exception as e:
            print(f"Error in send_code(): {str(e)}")
            return jsonify({"error": str(e)}), 500
        
        print(f"sending auth code to {phone_number}")

        if saved_client is None:
            status = await create_session(client, phone_number, phone_code_hash)
            if status == -1:
                return jsonify({"message": "error creating session"}), 500

        if user_id is not None:
            status = await set_auth_status(user_id, "auth_code")
            if status == 1:
                return jsonify({"error": "couldn't update auth_status"}), 500
        
        return "ok", 200

    except Exception as e:
        print(f"Error in send-code: {str(e)}")
        return jsonify({"error": str(e)}), 500