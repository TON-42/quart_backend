from quart import Blueprint, jsonify, request
from db import Session
from sqlalchemy.orm import joinedload
from models import User, Chat, ChatStatus
from services.user_service import create_user, set_auth_status
from services.chat_service import create_chat, add_chat_to_users
from services.session_service import create_session, session_exists, delete_session
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChat, PeerChannel
from utils import get_chat_id, count_words, connect_client, disconnect_client, print_chat
from bot import chat_sale
import os
import asyncio

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")


chat_route = Blueprint('chat_route', __name__)

@chat_route.route("/send-message", methods=["POST"])
async def send_message():
    data = await request.get_json()
    
    user_id = data.get("userId")
    phone_number = data.get("phone_number")
    if not phone_number:
        if not user_id:
            return jsonify("No phone_number and userId provided"), 400
    
    message = data.get("message")
    if not message:
        message = "Hello! The owner of this chat wants to sell the data of this chat.\nPlease click the button below to accept the sale and proceed to the bot:"
    else:
        message_for_second_user = (
            message + "\n\n"
            "https://t.me/chatpayapp_bot/chatpayapp"
        )

    selected_chats = data.get("chats", {})
    if not selected_chats:
        return jsonify("No chats were sent"), 400

    print(f"received: {phone_number}, {user_id}, {selected_chats}")

    saved_client = await session_exists(phone_number, user_id)
    if saved_client is None:
        print("Session does not exist")
        return jsonify("Session does not exist"), 500
    
    client = TelegramClient(StringSession(saved_client.id), API_ID, API_HASH)

    if await connect_client(client, phone_number, user_id) == -1:
        return jsonify({"error": "error in connecting to Telegram"}), 500
    
    if not await client.is_user_authorized():
        await disconnect_client(client, "Session is expired or user manually logged out")
        return jsonify("Session is expired or user manually logged out"), 500

    sender = await client.get_me()

    b_users = []
    chat_users = []
    for chat_details, words in selected_chats.items():
        try:
            # Parse chat_id and chat_name
            id_field = str(chat_details).strip("()")
            chat_id_str, chat_name_str = id_field.split(", '", 1)
            chat_id = int(chat_id_str)
            chat_name = chat_name_str[:-1]

            print(f"processing: (id: {chat_id}, name: {chat_name})")
            chat_id = chat_id or 123
            chat_name = chat_name or "Undefined"
            words = words or 123

            # Fetch the entity to ensure it's encountered by the library
            try:
                entity = await client.get_entity(chat_id)
            except ValueError as e:
                # Fetch dialogs to ensure the entity is cached
                await client.get_dialogs()
                entity = await client.get_entity(chat_id)

            users = await client.get_participants(entity)
            for user in users:
                await create_user(user.id, user.username, False)
                chat_users.append(user.id)
                b_users.append(user.username)

            chat_users.append(sender.id)
            private_chat_id = '_'.join(str(num) for num in sorted(chat_users))
            await create_chat(private_chat_id, chat_name, words, sender.id, chat_users, chat_id)
            
            # Call print_chat asynchronously without waiting for it to complete
            asyncio.create_task(print_chat(entity, chat_name, client))

            print(f"Sending message to {chat_name}")
            await client.send_message(entity, message_for_second_user, parse_mode="html")
            await add_chat_to_users(chat_users, private_chat_id)
            chat_users.clear()
        except Exception as e:
            if await client.is_user_authorized():
                await client.log_out()
            await disconnect_client(client, f"Error in send_message(): {str(e)}")
            await delete_session(phone_number, user_id)
            return {"error": str(e)}, 500
    
    status = await set_auth_status(sender.id, "default")
    if status == 1:
        await disconnect_client(client, "Couldn't update auth_status")
        return jsonify({"error": "couldn't update auth_status"}), 500
    return jsonify({"userB": b_users if b_users else None}), 200


@chat_route.route("/add-user-to-agreed", methods=["POST"])
async def add_user_to_agreed():
    session = Session()
    try:
        data = await request.get_json()
        print(f"/add-user-to-agreed received: {data}")
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
                user = session.query(User).options(
                    joinedload(User.chats)).filter(User.id == user_id).one()
            except Exception as e:
                print(f"Error in retrieving user from db: {str(e)}")
                continue

            # get chat
            try:
                chat = session.query(Chat).options(
                    joinedload(Chat.agreed_users),
                    joinedload(Chat.users)
                ).filter(Chat.id == chat_id).one()
            except Exception as e:
                print(f"Error in retrieving chats from db: {str(e)}")
                continue

            # if chat is already sold
            if chat.status == ChatStatus.sold:
                chat_status[chat_id] = "sold"
                continue

            for chat_user in chat.users:
                # if user exists in the chat 
                if chat_user.id == user_id:
                    for user_agreed in chat.agreed_users:
                        # if user has already agreed
                        if user_agreed.id == user_id:
                            break
                    chat.agreed_users.append(user)
                    chat_status[chat_id] = "pending"
                    break

            # if all users have agreed
            if len(chat.agreed_users) == len(chat.users):
                chat.status = ChatStatus.sold
                chat_status[chat_id] = "sold"
                await chat_sale(chat.users)
                print(f"chat {chat_id} is sold")
            session.commit()

        session.close()
        return jsonify(chat_status), 200
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500