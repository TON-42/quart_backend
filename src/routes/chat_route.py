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
from utils import get_chat_id, count_words, connect_client
from bot import chat_sale
import os

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
    message_for_second_user = (
        message + "\n\n"
        "https://t.me/chatpayapp_bot/chatpayapp"
    )

    selected_chats = data.get("chats", {})
    if not selected_chats:
        return jsonify("No chats were send"), 400

    print(f"received: {phone_number}, {selected_chats}")

    saved_client = await session_exists(phone_number, user_id)
    if saved_client is None:
        print("Session does not exist")
        return jsonify("Session does not exist"), 500
    
    client = TelegramClient(StringSession(saved_client.id), API_ID, API_HASH)

    if await connect_client(client, phone_number, user_id) == -1:
        return jsonify({"error": "error in connecting to Telegram"}), 500
    
    if not await client.is_user_authorized():
        print("Session is expired or user manually logged out")
        return jsonify("Session is expired or user manually logged out"), 500
    
    sender = await client.get_me()
    if not sender:
        print("User manually logged out")
        return jsonify("User manually logged out"), 500

    # TODO: organize this mess
    b_users = []
    chat_users = []
    for chat_details, words in selected_chats.items():
        try:
            # TODO: make data parsing as separate func or remove tuples
            # Extract chat_id and chat_name from 'id' field
            id_field = str(chat_details)
            id_field_clean = id_field.strip("()")
            chat_id_str, chat_name_str = id_field_clean.split(", '", 1)
            chat_id = int(chat_id_str)
            chat_name = chat_name_str[:-1]  # Remove the trailing single quote
            
            print(f"id: {chat_id}, name: {chat_name}")
            if not chat_id:
                print("Chat.id is not defined")
                chat_id = 123

            if not chat_name:
                print("Chat.name is not defined")
                chat_name = "Undefined"

            if not words:
                print("words is not defined")
                words = 123

            try:
                chat_entity = await client.get_entity(PeerChat(chat_id))
            except ValueError:
                chat_entity = await client.get_entity(PeerChannel(chat_id))
            
            users = await client.get_participants(chat_entity)
            
            for user in users:
                print(f"Creating {user.username} account")
                await create_user(user.id, user.username, False)
                chat_users.append(user.id)
                b_users.append(user.username)
        
            chat_users.append(sender.id)
            print(f"chat users: {chat_users}")
            
            private_chat_id = '_'.join(str(num) for num in sorted(chat_users))
            print(f"private_id {private_chat_id}")
    
            print(f"Creating {chat_name} chat")
            await create_chat(private_chat_id, chat_name, words, sender.id, chat_users, chat_id)
            print(f"Sending message to {chat_name}")
            await client.send_message(chat_id, message_for_second_user, parse_mode="html")
            print(f"Adding {chat_name} to {chat_users}")
            await add_chat_to_users(chat_users, private_chat_id)
            chat_users.clear()
        except Exception as e:
            print(f"Error in send_message(): {str(e)}")
            if await client.is_user_authorized():
                await client.log_out()
            await delete_session(phone_number, user_id)
            return {"error": str(e)}, 500
    
    status = await set_auth_status(sender.id, "default")
    if status == 1:
        return jsonify({"error": "couldn't update auth_status"}), 500

    return jsonify({"userB": b_users if b_users else None}), 200
