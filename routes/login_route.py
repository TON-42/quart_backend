from quart import Blueprint, jsonify, request
from db import Session
from shared import user_clients
from telethon.errors import SessionPasswordNeededError, PhoneNumberBannedError, PhoneNumberFloodError, PhoneNumberInvalidError, AuthRestartError, PhoneCodeExpiredError, PhoneCodeInvalidError, PhoneCodeEmptyError
from collections import defaultdict
from client_wrapper import ClientWrapper
from config import Config
from services.user_service import set_has_profile, set_auth_status
from models import User, Chat, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload

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
    
    # TODO: test if it works
    if phone_number in user_clients:
        if user_clients[phone_number].get_logged_in() == True and await user_clients[phone_number].get_client().get_me() is not None:
            print(f"{phone_number} is already logged in")
            return jsonify({"message": "user is already logged in"}), 409

    try:
        await user_clients[phone_number].get_client().sign_in(phone_number, auth_code)
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
        print(f"Error in sign_in(): {str(e)}")
        return jsonify({"error": str(e)}), 500

    print(f"{phone_number} is logged in")
    
    # save user id in the session
    sender = await user_clients[phone_number].get_client().get_me()
    user_clients[phone_number].set_id(sender.id)
    user_clients[phone_number].set_logged_in(True)

    # TODO: make it as a separate function
    try:
        session = Session()
        user = (
            session.query(User)
            .options(joinedload(User.chats).joinedload(Chat.users))
            .filter(User.id == sender.id)
            .first()
        )
        
        if user is None:
            session.close()
            return jsonify({"message": f"User with id {sender.id} does not exist"}), 404
        
        chat_ids = [chat.id for chat in user.chats]
        print(f"User {sender.id} previously sold chats: {chat_ids}")
        session.close()
    except Exception as e:
        session.close()
        print(f"Error before sign_in() {str(e)}")
        return {"error": str(e)}, 500

    # TODO: handle this error properly
    status = await set_has_profile(sender.id, True)
    if status == 1:
        return jsonify({"error": "couldn't set has_profile to True"}), 500
    
    count = 0
    res = defaultdict(int)
    chat_users = []

    try:
        if await user_clients[phone_number].get_client().is_user_authorized():
            dialogs = await user_clients[phone_number].get_client().get_dialogs()
            for dialog in dialogs:
                if dialog.id < 0 or dialog.entity.bot == True or dialog.id == 777000:
                    continue
    
                # TODO: make a separate func
                chat_users.clear()
                users = await user_clients[phone_number].get_client().get_participants(chat_id)
                for user in users:
                    chat_users.append(user.id)
                chat_users.append(sender.id)
                private_chat_id = '_'.join(str(num) for num in sorted(chat_users))
                if private_chat_id in chat_ids:
                    print(f"Chat {dialog.name} is already sold")
                    continue
        
                # TODO: think about the limit of chats
                count += 1
                if count > 15:
                    break

                print(f"{dialog.name}, {dialog.id}")
                # TODO: is there a better way to count words
                async for message in (
                    user_clients[phone_number].get_client().iter_messages(dialog.id)
                ):
                    if message.text is not None:
                        words = message.text.split()
                        res[(dialog.id, dialog.name)] += len(words)
                        if res[(dialog.id, dialog.name)] > 2000:
                            break
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
            # user entered from browser
            print(f"{phone_number} entered from browser")

        if phone_number in user_clients:
            if user_clients[phone_number].get_logged_in() == True and await user_clients[phone_number].get_client().get_me() is not None:
                print(f"{phone_number} is already logged in")
                return jsonify({"message": "user is already logged in"}), 409
            # TODO: here we delete session to send code again but this could lead to spam
            del user_clients[phone_number]

        print(f"sending auth code to {phone_number}")

        if phone_number not in user_clients:
            user_clients[phone_number] = ClientWrapper(phone_number, Config.API_ID, Config.API_HASH)
            try:
                await user_clients[phone_number].get_client().connect()
            except Exception as e:
                print(f"Error in connect(): {str(e)}")
                del user_clients[phone_number]
                return jsonify({"error": str(e)}), 500

        try:
            await user_clients[phone_number].get_client().send_code_request(phone_number)
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
            await user_clients[phone_number].get_client().send_code_request(phone_number)
        except Exception as e:
            print(f"Error in send_code(): {str(e)}")
            return jsonify({"error": str(e)}), 500
        
        if user_id is not None:
            status = await set_auth_status(user_id, "auth_code")
            if status == 1:
                return jsonify({"error": "couldn't update auth_status"}), 500
        
        return "ok", 200

    except Exception as e:
        print(f"Error in send-code: {str(e)}")
        return jsonify({"error": str(e)}), 500