from quart import Quart, jsonify, request
from quart_cors import cors
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    Bot,
)
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    ChatMemberHandler,
    PollHandler,
    ContextTypes,
)
from telethon import TelegramClient, events
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, AuthRestartError
from dotenv import load_dotenv, dotenv_values
import os
import enum
import logging
import asyncpg
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from models import User, Chat, ChatStatus
from debug_routes import debug_routes
from db import Session
import asyncio
from quart_jwt_extended import JWTManager, create_access_token, jwt_required

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("BOT_TOKEN")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

bot: Bot = Bot(token=TOKEN)

app = Quart(__name__)
app = cors(app, allow_origin="*")

app.register_blueprint(debug_routes)

app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

jwt = JWTManager(app)

user_clients = {}


async def check_session_expiry():
    while True:
        # Iterate over user_clients to check each session
        for phone_number, client_wrapper in list(user_clients.items()):
            # Calculate the difference between current time and session creation time
            print(f"Session for: {phone_number} is active")
            time_difference = datetime.now() - client_wrapper.created_at
            if time_difference >= timedelta(minutes=20):
                print(f"Session for {phone_number} has expired.")
                del user_clients[phone_number]

        # Wait for 5 minute before checking again
        await asyncio.sleep(300)



@app.route('/access', methods=['POST'])
async def access():
    data = await request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    
    # Replace with your user authentication logic
    if username != API_USERNAME or password != API_PASSWORD:
        return jsonify({"msg": "Bad username or password"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.errorhandler(401)
async def custom_401(error):
    return jsonify({"msg": "Unauthorized access"}), 401

@app.before_serving
async def startup():
    app.add_background_task(check_session_expiry)


@app.after_serving
async def shutdown():
    for task in app.background_tasks:
        task.cancel()


class ClientWrapper:
    def __init__(self, phone_number, api_id, api_hash):
        self.client = TelegramClient(phone_number, api_id, api_hash)
        self.created_at = datetime.now()
        self.id = 0

    def get_client(self):
        return self.client

    def get_creation_time(self):
        return self.created_at

    def get_id(self):
        return self.client

    def set_id(self, new_id):
        self.id = new_id


# @app.route("/get-sessions", methods=["GET"])
# async def get_sessions():
#     print(len(user_clients))
#     try:
#         sessions = []
#         for phone_number, client_wrapper in user_clients.items():
#             session_info = {
#                 "phone_number": phone_number,
#                 "created_at": client_wrapper.get_creation_time().isoformat()
#             }
#             sessions.append(session_info)

#         return jsonify(sessions), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/initialize-client", methods=["GET"])
# async def initialize_client():
#     phone_number = request.args.get("phone_number", "")

#     if phone_number not in user_clients:
#         user_clients[phone_number] = ClientWrapper(phone_number, API_ID, API_HASH)

#     client_info = {
#         "phone_number": phone_number,
#         "created_at": user_clients[phone_number].get_creation_time().isoformat()
#     }
#     print(len(user_clients))
#     return jsonify(client_info)


async def start(update: Update, context):
    print("start command received")
    update.message.reply_text("Open the miniapp to find out more!")


async def create_user(sender, profile):
    session = Session()
    status = 0
    try:
        # Query the database to check if a user with the provided ID exists
        existing_user = session.query(User).filter(User.id == sender.id).one()
        print("User already exists")
    except NoResultFound:
        new_user = User(
            id=sender.id, name=sender.username, has_profile=profile, words=0
        )
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "has_profile": new_user.has_profile,
            "words": new_user.words,
        }

        print(user_data)
        session.add(new_user)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        status = 1
    finally:
        session.close()
        return status


async def create_chat(chat_id, chat_name, words_number, sender_id, chat_users):
    session = Session()
    status = 0
    try:
        # Query the database to check if a chat with the provided ID exists
        existing_chat = session.query(Chat).filter(Chat.id == chat_id).one()
        print("Chat already exists")
    except NoResultFound:
        new_chat = Chat(
            id=chat_id,
            name=chat_name,
            words=words_number,
            status=ChatStatus.pending,
            lead_id=sender_id,
            full_text="None",
        )

        lead = session.query(User).filter(User.id == sender_id).one()
        new_chat.lead = lead

        agreed_user_ids = [sender_id]
        agreed_users = session.query(User).filter(User.id.in_(agreed_user_ids)).all()
        new_chat.agreed_users.extend(agreed_users)

        all_users = (
            session.query(User).filter(User.id.in_([sender_id] + chat_users)).all()
        )
        new_chat.users.extend(all_users)

        session.add(new_chat)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        status = 1
    finally:
        session.close()
        return status


async def add_chat_to_users(users_id, chat_id):
    status = 0
    try:
        session = Session()

        # get 1 chat
        chat = session.query(Chat).filter(Chat.id == chat_id).one()
        # get all related users
        users = session.query(User).filter(User.id.in_(users_id)).all()

        # add the chat to each user
        for user in users:
            if chat not in user.chats:
                user.chats.append(chat)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
        status = 1
    finally:
        session.close()
        return status


@app.route("/health", methods=["GET"])
async def health():
    app.logger.info("Health check endpoint called")
    return "ok", 200


@app.route("/hello", methods=["GET"])
@jwt_required
async def hello_world():
    print("hello endpoint!!")
    return jsonify({"message": "Hello, World!"})


@app.route('/login', methods=['POST'])
@jwt_required
async def login():
    print("entered login")
    data = await request.get_json()
    auth_code = data.get("code")
    print("auth code:")
    print(auth_code)
    phone_number = data.get("phone_number")
    print(phone_number)

    try:
        await user_clients[phone_number].get_client().sign_in(phone_number, auth_code)
    except SessionPasswordNeededError:
        print("two-steps verification is active")
        await user_clients[phone_number].get_client().disconnect()
        del user_clients[phone_number]
        return "401"
    except Exception as e:
        print(f"Error: {str(e)}")
        await user_clients[phone_number].get_client().disconnect()
        del user_clients[phone_number]
        return {"error": str(e)}, 500

    # save user id in the session
    sender = await user_clients[phone_number].get_client().get_me()
    user_clients[phone_number].set_id(sender.id)

    count = 0
    bot_id = 0
    res = defaultdict(int)

    try:
        if await user_clients[phone_number].get_client().is_user_authorized():
            dialogs = await user_clients[phone_number].get_client().get_dialogs()
            for dialog in dialogs:
                if dialog.id < 0 or dialog.id == 777000:
                    continue

                # users = await user_clients[phone_number].get_client().get_participants(dialog.id)
                # if (len(users) > 5):
                #     continue

                count += 1
                if count > 15:
                if count > 15:
                    break
                print(f"{dialog.name}, {dialog.id}")
                async for message in (
                    user_clients[phone_number].get_client().iter_messages(dialog.id)
                ):
                    if message.text is not None:
                        words = message.text.split()
                        res[(dialog.id, dialog.name)] += len(words)
                        if res[(dialog.id, dialog.name)] > 2000:
                            break
    except Exception as e:
        print(f"Error: {str(e)}")
        await user_clients[phone_number].get_client().disconnect()
        del user_clients[phone_number]
        return {"error": str(e)}, 500

    res_json_serializable = {str(key): value for key, value in res.items()}

    # Print the JSON-serializable dictionary
    print(res_json_serializable)

    return jsonify(res_json_serializable), 200


@app.route("/send-message", methods=["POST"])
@jwt_required
async def send_message():
    data = await request.get_json()
    phone_number = data.get("phone_number")
    sender = await user_clients[phone_number].get_client().get_me()
    sender_id = sender.id
    print(sender_id)

    status = await create_user(sender, True)
    # if (status == 1):
    #     return jsonify("Could not create a user"), 500

    selected_chats = data.get("chats", [])
    print("received from front-end:")
    print(selected_chats)

    b_users = []
    chat_users = []

    for chat_details in selected_chats:
        try:
            # Extract chat_id and chat_name from 'id' field
            id_field = chat_details["id"]
            chat_id_str, chat_name_str = id_field[1:-1].split(", '")
            chat_id = int(chat_id_str)
            chat_name = chat_name_str[:-1]

            if not chat_id:
                print("Chat.id is not defined")
                chat_id = 123

            if not chat_name:
                print("Chat.name is not defined")
                chat_name = "Undefined"

            words = chat_details["value"]
            if not words:
                print("words is not defined")
                words = 123

            users = (
                await user_clients[phone_number].get_client().get_participants(chat_id)
            )
            for user in users:
                if user.username is not None:
                    await create_user(user, False)
                    chat_users.append(user.id)
                    b_users.append(user.username)
                    print(user.username)

            message_for_second_user = (
                "Hello! The owner of this chat wants to sell the data of this chat. "
                "Please click the button below to accept the sale and proceed to the bot:\n\n"
                "https://t.me/chatpayapp_bot/chatpayapp"
            )
            await create_chat(chat_id, chat_name, words, sender_id, chat_users)
            await user_clients[phone_number].get_client().send_message(
                chat_id, message_for_second_user, parse_mode="html"
            )
            await add_chat_to_users(chat_users + [sender_id], chat_id)
            chat_users.clear()
        except Exception as e:
            print(f"Error: {str(e)}")
            await user_clients[phone_number].get_client().disconnect()
            del user_clients[phone_number]
            return {"error": str(e)}, 500

    await user_clients[phone_number].get_client().disconnect()
    del user_clients[phone_number]
    return jsonify({"userB": b_users if b_users else None}), 200


@app.route("/send-code", methods=["POST"])
@jwt_required
async def send_code():
    print("entered send_code")
    data = await request.get_json()
    phone_number = data.get("phone_number")
    print(phone_number)
    if phone_number is None:
        return jsonify({"error": "phone_number is missing"}), 400

    user_clients[phone_number] = ClientWrapper(phone_number, API_ID, API_HASH)

    try:
        await user_clients[phone_number].get_client().connect()
    except OSError as e:
        del user_clients[phone_number]
        return {"error": str(e)}, "400"

    try:
        await user_clients[phone_number].get_client().send_code_request(phone_number)
    except PhoneNumberInvalidError as e:
        await user_clients[phone_number].get_client().disconnect()
        del user_clients[phone_number]
        return {"error": str(e)}, "404"
    except (AuthRestartError) as e:
        await user_clients[phone_number].get_client().send_code_request(phone_number)
    except Exception as e:
        await user_clients[phone_number].get_client().disconnect()
        del user_clients[phone_number]
        return {"error": str(e)}, "400"

    return "ok", 200


@app.route("/get-user", methods=["POST"])
@jwt_required
async def get_user():
    try:
        data = await request.get_json()

        user_id = data.get("userId")
        if user_id is None:
            return jsonify({"error": "userId is missing"}), 400

        # Create a session
        session = Session()

        # Query all users
        user = (
            session.query(User)
            .options(joinedload(User.chats).joinedload(Chat.users))
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            session.close()
            return jsonify({"message": f"User with id {user_id} does not exist"}), 404

        for chat in user.chats:
            chat.agreed_users

        # Close the session
        session.close()

        return jsonify(
            {
                "id": user.id,
                "name": user.name,
                "has_profile": user.has_profile,
                "words": user.words,
                "chats": [
                    {
                        "id": chat.id,
                        "name": chat.name,
                        "words": chat.words,
                        "status": chat.status.name,
                        "lead_id": chat.lead_id,
                        "agreed_users": [
                            agreed_user.id for agreed_user in chat.agreed_users
                        ],
                        "users": [user.id for user in chat.users],
                    }
                    for chat in user.chats
                ],
            }
        )

    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500


@app.route("/is-active", methods=["POST"])
@jwt_required
async def is_active():
    try:
        data = await request.get_json()

        user_id = data.get("userId")
        if user_id is None:
            return jsonify({"error": "userId is missing"}), 400

        for phone_number, client_wrapper in user_clients.items():
            if user_id == client_wrapper.get_id():
                return "ok", 200
        return "Not found", 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
# dispatcher.add_handler(ChatMemberHandler(vote, ChatMemberHandler.MY_CHAT_MEMBER))
# dispatcher.add_handler(PollHandler(poll_monitor))


@app.route("/webhook", methods=["POST"])
async def webhook():
    print("entered webhook")
    app.logger.info("Webhook received")
    if request.method == "POST":
        data = await request.get_json()
        update = Update.de_json(data, bot)
        update.message.reply_text("Open the miniapp to find out more!")
        dispatcher.process_update(update)
    return "ok"


if __name__ == "__main__":
    app.run(port=8080)
