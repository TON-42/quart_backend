from quart import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.types import User as TelegramUser, InputPeerUser
from db import get_sqlalchemy_session
from models import User, Chat, ChatStatus, ChatFullText
from services.user_service import create_user, set_auth_status
from services.chat_service import create_chat, add_chat_to_users
from services.session_service import fetch_user_session, delete_session
from utils import (
    connect_client,
    disconnect_client,
    print_chat,
)
from bot import chat_sale
import asyncio
import logging
from config import Config

from models import ChatStatus


logger = logging.getLogger(__name__)


chat_route = Blueprint("chat_route", __name__)


@chat_route.route("/send-message", methods=["POST"])
async def send_message():
    data = await request.get_json()

    user_id = data.get("userId")
    phone_number = data.get("phone_number")
    if not phone_number and not user_id:
        return jsonify("No phone_number and userId provided"), 400
    message = data.get(
        "message",
        "Hello! The owner of this chat wants to sell the data of this chat.\nPlease click the button below to accept the sale and proceed to the bot:",
    )
    message_invitee = message + "\n\nhttps://t.me/chatpayapp_bot/chatpayapp"

    selected_chats = data.get("chats", {})
    if not selected_chats:
        return jsonify("No chats were sent"), 400

    logger.info(f"received: {phone_number}, {user_id}, {selected_chats}")

    async with get_sqlalchemy_session() as db_session:
        user_db_session = await fetch_user_session(phone_number, user_id, db_session)
        if user_db_session is None:
            logger.error("Session does not exist")
            return jsonify("Session does not exist"), 500

        client = TelegramClient(
            StringSession(user_db_session.id), Config.API_ID, Config.API_HASH
        )

        if await connect_client(client, phone_number, user_id) == -1:
            return jsonify({"error": "error in connecting to Telegram"}), 500

        if not await client.is_user_authorized():
            await disconnect_client(
                client, "Session is expired or user manually logged out"
            )
            return jsonify("Session is expired or user manually logged out"), 500

        sender = await client.get_me()
        if isinstance(sender, TelegramUser):
            sender_id = sender.id
        elif isinstance(sender, InputPeerUser):
            sender_id = sender.user_id
        else:
            await disconnect_client(client, "Unknown type returned by get_me()")
            return jsonify({"error": "Unknown type returned by get_me()"}), 500

        chat_user_names = []
        chat_user_ids = []
        for chat_details, words in selected_chats.items():
            try:
                # Parse chat_id and chat_name
                id_field = str(chat_details).strip("()")
                chat_id_str, chat_name_str = id_field.split(", '", 1)
                chat_id = int(chat_id_str)
                chat_name = chat_name_str[:-1]

                logger.info(f"processing: (id: {chat_id}, name: {chat_name})")
                chat_id = chat_id or 123
                chat_name = chat_name or "Undefined"
                words = words or 123

                # Fetch the entity to ensure it's encountered by the library
                try:
                    chat_entity = await client.get_entity(chat_id)
                    if isinstance(chat_entity, list):
                        chat_entity = chat_entity[0]
                except ValueError as e:
                    # Fetch dialogs to ensure the entity is cached
                    await client.get_dialogs()
                    chat_entity = await client.get_entity(chat_id)
                    if isinstance(chat_entity, list):
                        chat_entity = chat_entity[0]

                chat_users = await client.get_participants(chat_entity)
                for user in chat_users:
                    await create_user(user.id, user.username, False)
                    chat_user_ids.append(user.id)
                    chat_user_names.append(user.username)

                chat_user_ids.append(sender_id)
                private_chat_id = "_".join(str(num) for num in sorted(chat_user_ids))
                await create_chat(
                    private_chat_id, chat_name, words, sender_id, chat_user_ids, chat_id
                )
                # Call print_chat asynchronously without waiting for it to complete
                asyncio.create_task(print_chat(chat_entity, chat_name, client))

                logger.info(f"Sending message to {chat_name}")
                await client.send_message(
                    chat_entity, message_invitee, parse_mode="html"
                )

                await add_chat_to_users(chat_user_ids, private_chat_id)
                chat_user_ids.clear()
            except Exception as e:
                if await client.is_user_authorized():
                    await client.log_out()
                await disconnect_client(client, f"Error in send_message(): {str(e)}")
                await delete_session(phone_number, user_id)
                return {"error": str(e)}, 500

        status = await set_auth_status(sender_id, "default")
        if status == 1:
            await disconnect_client(client, "Couldn't update auth_status")
            return jsonify({"error": "couldn't update auth_status"}), 500
        return (
            jsonify({"user names": chat_user_names if chat_user_names else None}),
            200,
        )


@chat_route.route("/add-user-to-agreed", methods=["POST"])
async def add_user_to_agreed():
    async with get_sqlalchemy_session() as db_session:
        try:
            data = await request.get_json()
            logger.info(f"/add-user-to-agreed received: {data}")
            if not isinstance(data, list):
                return jsonify({"error": "Input data should be an array"}), 400
            chat_status = {}
            for entry in data:
                user_id = entry.get("userId")
                chat_id = entry.get("chatId")

                if user_id is None or chat_id is None:
                    chat_status[chat_id] = "error"
                    continue

                chat_status[chat_id] = "error"

                # get user
                try:
                    user = (
                        db_session.query(User)
                        .options(joinedload(User.chats))
                        .filter(User.id == user_id)
                        .one()
                    )
                except Exception as e:
                    logger.error(f"Error in retrieving user from db: {str(e)}")
                    continue

                # get chat
                try:
                    chat = (
                        db_session.query(Chat)
                        .options(joinedload(Chat.agreed_users), joinedload(Chat.users))
                        .filter(Chat.id == chat_id)
                        .one()
                    )
                except Exception as e:
                    logger.error(f"Error in retrieving chats from db: {str(e)}")
                    continue

                # if chat is already sold
                print(f"Type of chat.status: {type(chat.status)}")
                print(f"Value of chat.status: {chat.status}")
                print(f"Type of ChatStatus.sold: {type(ChatStatus.sold)}")
                print(f"Value of ChatStatus.sold: {ChatStatus.sold}")
                print(f"Type of ChatStatus.sold.value: {type(ChatStatus.sold.value)}")
                print(f"Value of ChatStatus.sold.value: {ChatStatus.sold.value}")

                if chat.status == ChatStatus.sold:
                    chat_status[chat_id] = "sold"
                    continue

                # Check if the user is in the chat
                if user not in chat.users:
                    logger.error(f"User {user_id} is not in chat {chat_id}")
                    chat_status[chat_id] = "error"
                    continue

                # Check if the user has already agreed
                if user in chat.agreed_users:
                    chat_status[chat_id] = "pending"
                else:
                    # Add the user to agreed_users
                    chat.agreed_users.append(user)
                    chat_status[chat_id] = "pending"

                # if all users have agreed
                if len(chat.agreed_users) == len(chat.users):
                    # chat.status = cast(ChatStatus, ChatStatus.sold)
                    # assert isinstance(chat.status, ChatStatus)
                    chat.status = ChatStatus.sold
                    chat_status[chat_id] = "sold"
                    await chat_sale(chat.users)
                    logger.info(f"chat {chat_id} is sold")
                    for user in chat.users:
                        logger.info(f"{user} received {chat.words} $WORD")
                        user.words += chat.words

                    # Check if the user is logged in and has an open session
                    user_db_session = await fetch_user_session(
                        None, user.id, db_session
                    )
                    if user_db_session is None:
                        logger.error(
                            "Session does not exist: Chat is sold, but has not been fetched!"
                        )
                        # we still return 200, because the chat is sold
                        continue

                    client = TelegramClient(
                        StringSession(user_db_session.id),
                        Config.API_ID,
                        Config.API_HASH,
                    )
                    if await connect_client(client, None, user.id) == -1:
                        logger.error("Error in connecting to Telegram")
                        # we still return 200, because the chat is sold
                        continue
                    if not await client.is_user_authorized():
                        await disconnect_client(
                            client, "Session is expired or user manually logged out"
                        )
                        # we still return 200, because the chat is sold
                        continue
                    # Retrieve chat entity
                    try:
                        chat_entity = await client.get_entity(chat.telegram_id.value)
                        if isinstance(chat_entity, list):
                            chat_entity = chat_entity[0]
                    except ValueError:
                        await client.get_dialogs()
                        chat_entity = await client.get_entity(chat.telegram_id.value)
                        if isinstance(chat_entity, list):
                            chat_entity = chat_entity[0]

                    # Fetch and save chat text to ChatFullText
                    full_text = ""
                    async for message in client.iter_messages(chat_entity):
                        if message.text:
                            full_text += message.text + "\n"

                    chat_full_text = ChatFullText(chat_id=chat.id, full_text=full_text)
                    db_session.add(chat_full_text)

                    await disconnect_client(client, f"Fetched and saved chat {chat_id}")
                    chat_status[chat_id] = "fetched"

                db_session.commit()

            return jsonify(chat_status), 200
        except Exception as e:
            logger.error(f"Error in /add-user-to-agreed: {str(e)}")
            return jsonify({"error": str(e)}), 500
