from quart import Quart, jsonify, request
from quart_cors import cors
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, AuthRestartError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from models import User, Chat, ChatStatus
from debug_routes import debug_routes
from db import Session
import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types

commands = (
    "📝 /start - Start the bot\n"
    "❓ /help - Get help on how to use the bot\n"
    "📷 /image - Send an image\n"
    "📦 /package - Example command for package\n"
    "🔄 /update - Update command\n"
    "❌ /delete - Delete command\n"
    "⚙️ /settings - Settings command\n"
)

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("BOT_TOKEN")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

bot = AsyncTeleBot(TOKEN)
app = Quart(__name__)
app = cors(app, allow_origin="*")

app.register_blueprint(debug_routes)

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
                await user_clients[phone_number].get_client().log_out()
                del user_clients[phone_number]

        # Wait for 5 minute before checking again
        await asyncio.sleep(300)


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


@app.route("/get-sessions", methods=["GET"])
async def get_sessions():
    print(len(user_clients))
    try:
        sessions = []
        for phone_number, client_wrapper in user_clients.items():
            session_info = {
                "phone_number": phone_number,
                "created_at": client_wrapper.get_creation_time().isoformat()
            }
            sessions.append(session_info)

        return jsonify(sessions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# async def text_messages(update: Update, context: CallbackContext):
#     print("text message")
#     update.message.reply_text('List of avaliable commands:\n' + commands)

async def create_user(user_id, username, profile):
    session = Session()
    try:
        # Query the database to check if a user with the provided ID exists
        existing_user = session.query(User).filter(User.id == user_id).one()
        # print("User already exists")
    except NoResultFound:
        new_user = User(
            id=user_id, name=username, has_profile=profile, words=0
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
    finally:
        session.close()


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

async def update_profile(user_id, has_profile):
    session = Session()
    status = 0
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.has_profile = has_profile
        session.commit()
    except NoResultFound:
        print(f"User with ID {user_id} not found")
        status = 1
    except Exception as e:
        print(f"Error updating username or profile: {str(e)}")
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
async def hello_world():
    print("hello endpoint!!")
    return jsonify({"message": "Hello, World!"})


@app.route('/login', methods=['POST'])
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
        await user_clients[phone_number].get_client().log_out()
        del user_clients[phone_number]
        return "401"
    except Exception as e:
        print(f"Error: {str(e)}")
        await user_clients[phone_number].get_client().log_out()
        del user_clients[phone_number]
        return {"error": str(e)}, 500

    # save user id in the session
    sender = await user_clients[phone_number].get_client().get_me()
    user_clients[phone_number].set_id(sender.id)

    count = 0
    res = defaultdict(int)

    try:
        if await user_clients[phone_number].get_client().is_user_authorized():
            dialogs = await user_clients[phone_number].get_client().get_dialogs()
            for dialog in dialogs:
                if dialog.id < 0 or dialog.id == 777000:
                    continue
    
                count += 1
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
        await user_clients[phone_number].get_client().log_out()
        del user_clients[phone_number]
        return {"error": str(e)}, 500

    res_json_serializable = {str(key): value for key, value in res.items()}

    # Print the JSON-serializable dictionary
    print(res_json_serializable)
    return jsonify(res_json_serializable), 200


@app.route("/send-message", methods=["POST"])
async def send_message():
    data = await request.get_json()
    phone_number = data.get("phone_number")
    sender = await user_clients[phone_number].get_client().get_me()
    sender_id = sender.id

    message = data.get("message")
    if not message:
        message = "Hello! The owner of this chat wants to sell the data of this chat.\nPlease click the button below to accept the sale and proceed to the bot:"
    
    status = await update_profile(sender.id, True)
    if (status == 1):
        return jsonify("Could not create a user"), 500

    selected_chats = data.get("chats", {})
    if not selected_chats:
        print("No chats received from front-end.")
        return jsonify("No chats were send"), 400

    print("received from front-end:")
    print(selected_chats)

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
            await create_chat(chat_id, chat_name, words, sender_id, chat_users)
            await user_clients[phone_number].get_client().send_message(
                chat_id, message_for_second_user, parse_mode="html"
            )
            await add_chat_to_users(chat_users + [sender_id], chat_id)
            chat_users.clear()
        except Exception as e:
            print(f"Error: {str(e)}")
            await user_clients[phone_number].get_client().log_out()
            del user_clients[phone_number]
            return {"error": str(e)}, 500

    return jsonify({"userB": b_users if b_users else None}), 200


@app.route("/send-code", methods=["POST"])
async def send_code():
    print("entered send_code")
    data = await request.get_json()
    phone_number = data.get("phone_number")
    print(phone_number)
    if phone_number is None:
        return jsonify({"error": "phone_number is missing"}), 400
    
    if phone_number in user_clients:
        await user_clients[phone_number].get_client().log_out()
        del user_clients[phone_number]

    user_clients[phone_number] = ClientWrapper(phone_number, API_ID, API_HASH)

    try:
        await user_clients[phone_number].get_client().connect()

    except OSError as e:
        del user_clients[phone_number]
        return {"error": str(e)}, "400"

    try:
        await user_clients[phone_number].get_client().send_code_request(phone_number)
    except PhoneNumberInvalidError as e:
        await user_clients[phone_number].get_client().log_out()
        del user_clients[phone_number]
        return {"error": str(e)}, "404"
    except (AuthRestartError) as e:
        await user_clients[phone_number].get_client().send_code_request(phone_number)
    except Exception as e:
        await user_clients[phone_number].get_client().log_out()
        del user_clients[phone_number]
        return {"error": str(e)}, "400"

    return "ok", 200


@app.route("/get-user", methods=["POST"])
async def get_user():
    try:
        data = await request.get_json()

        user_id = data.get("userId")
        if user_id is None:
            return jsonify({"error": "userId is missing"}), 400
        
        username = data.get("username", "None")
        print(f"get-user: {username}")
        try:
            await create_user(user_id, username, False)
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return jsonify({"error": "Internal error"}), 500
        
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

@app.route("/add-user-to-agreed", methods=["POST"])
async def add_user_to_agreed():
    session = Session()
    try:
        data = await request.get_json()

        user_id = data.get("userId")
        if user_id is None:
            return jsonify({"error": "userId is missing"}), 400
        
        chat_id = data.get("chatId")
        if chat_id is None:
            return jsonify({"error": "chatId is missing"}), 400
        
        user = session.query(User).options(
            joinedload(User.chats)).filter(User.id == user_id).one()

        chat = session.query(Chat).options(
            joinedload(Chat.agreed_users),
            joinedload(Chat.users)
        ).filter(Chat.id == chat_id).one()

        for chat_user in chat.users:
            # if user exists in the chat 
            if chat_user.id == user_id:
                for user_agreed in chat.agreed_users:
                    # if user has already agreed
                    if user_agreed.id == user_id:
                        session.close()
                        return "User already agreed", 200
                chat.agreed_users.append(user)
                break
        # TODO: add tokens?
        # if all users have agreed
        if len(chat.agreed_users) == len(chat.users):
            chat.status = ChatStatus.sold
            session.commit()
            session.close()
            return jsonify({"success": "All users have agreed"}), 202
        else:
            session.commit()
            session.close()
            return "ok", 200
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500

@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        print("POST")
        data = await request.get_json()
        await bot.process_new_updates([data])
    return "ok"

@bot.message_handler(commands=['start'])
async def start(message):
    print("start command")
    chat_id = message.chat.id
    image_url = 'https://cdn.dorahacks.io/static/files/1901b1bf8a530aeeb65557744999b2d7.png'
    caption = (
        "**ChatPay** provides to users an easy way to **monetise** their Telegram chats by bundling them into AI training datasets.\n\n"
        "1. Choose the chats you want to submit as AI training datasets"
        "2. Get your estimated payout per each chat straight in the Telegram mini-app"
        "3. Hold on tight while your payout arrives.\n\n"
        "**Your data, your money, your consent**\n _Chats are monetised only if all chat group members give full consent._\n\n"
        "Our business model is based on:\n"
        "- Gathering chat user data (text initially, with audio, video and photos coming later).\n"
        "- Anonymising data by stripping it of all identifiers.\n"
        "- Tagging data and bundling it into datasets.\n"
        "- Selling datasets to LLM vendors to help train AI and chatbot models.\n\n"
        "_We work transparently by taking only a 25% cut of the sales and royalties, while letting users keep the lion's share of their earnings. A utility token will be coming soon, allowing us to do payouts for users. Token allocation for the team, early supporters, and testers is in our roadmap_"
    )
    await bot.send_photo(chat_id, image_url, caption, parse_mode='md')

@bot.message_handler(content_types=['text'])
async def message_reply(message):
    print("text message")
    await bot.reply_to(message, 'List of avaliable commands:\n' + commands)


if __name__ == "__main__":
    app.run(port=8080)

# from quart_jwt_extended import JWTManager, create_access_token, jwt_required
# app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

# jwt = JWTManager(app)

# @app.route('/access', methods=['POST'])
# async def access():
#     data = await request.get_json()
#     username = data.get('username', None)
#     password = data.get('password', None)
    
#     # Replace with your user authentication logic
#     if username != API_USERNAME or password != API_PASSWORD:
#         return jsonify({"msg": "Bad username or password"}), 401
    
#     access_token = create_access_token(identity=username)
#     return jsonify(access_token=access_token), 200

# @app.errorhandler(401)
# async def custom_401(error):
#     return jsonify({"msg": "Unauthorized access"}), 401


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
