from quart import Blueprint, jsonify, request
from db import Session
from sqlalchemy.orm import joinedload
from models import User, Chat, ChatStatus
from shared import user_clients
from services.user_service import create_user, update_profile
from services.chat_service import create_chat, add_chat_to_users


chat_route = Blueprint('chat_route', __name__)

@chat_route.route("/send-message", methods=["POST"])
async def send_message():
    data = await request.get_json()
    
    phone_number = data.get("phone_number")
    if not phone_number:
        return jsonify("No phone_number provided"), 400
    
    message = data.get("message")
    if not message:
        message = "Hello! The owner of this chat wants to sell the data of this chat.\nPlease click the button below to accept the sale and proceed to the bot:"

    selected_chats = data.get("chats", {})
    if not selected_chats:
        return jsonify("No chats were send"), 400

    sender = await user_clients[phone_number].get_client().get_me()
    
    # TODO: rename update_profile, it just sets has_profile
    status = await update_profile(sender.id, True)
    if (status == 1):
        return jsonify("Could not create a user"), 500


    print("received from front-end:")
    print(selected_chats)

    # TODO: organize this mess
    b_users = []
    chat_users = []
    for chat_details, words in selected_chats.items():
        try:
            # Extract chat_id and chat_name from 'id' field
            id_field = str(chat_details)
            
            # Remove the surrounding parentheses
            id_field_clean = id_field.strip("()")
            
            # Split the cleaned id_field by ", '"
            chat_id_str, chat_name_str = id_field_clean.split(", '", 1)
            
            # Convert chat_id_str to an integer and clean chat_name_str
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

            users = (
                await user_clients[phone_number].get_client().get_participants(chat_id)
            )
            for user in users:
                if user.username is not None:
                    await create_user(user.id, user.username, False)
                    chat_users.append(user.id)
                    b_users.append(user.username)
                    print(user.username)

            message_for_second_user = (
                message + "\n\n"
                "https://t.me/chatpayapp_bot/chatpayapp"
            )
            await create_chat(chat_id, chat_name, words, sender.id, sender.username, chat_users)
            await user_clients[phone_number].get_client().send_message(
                chat_id, message_for_second_user, parse_mode="html"
            )
            await add_chat_to_users(chat_users + [sender.id], chat_id)
            chat_users.clear()
        except Exception as e:
            print(f"Error: {str(e)}")
            await user_clients[phone_number].get_client().log_out()
            del user_clients[phone_number]
            return {"error": str(e)}, 500

    return jsonify({"userB": b_users if b_users else None}), 200

@chat_route.route("/add-user-to-agreed", methods=["POST"])
async def add_user_to_agreed():
    session = Session()
    try:
        data = await request.get_json()
        print(f"add-user-to-agreed: {data}")
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
                print(f"Error: {str(e)}")
                continue

            # get chat
            try:
                chat = session.query(Chat).options(
                    joinedload(Chat.agreed_users),
                    joinedload(Chat.users)
                ).filter(Chat.id == chat_id).one()
            except Exception as e:
                print(f"Error: {str(e)}")
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
            session.commit()

        session.close()
        return jsonify(chat_status), 200
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500