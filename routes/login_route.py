from quart import Blueprint, jsonify, request
from shared import user_clients
from telethon.errors import SessionPasswordNeededError, PhoneNumberBannedError, PhoneNumberFloodError,
PhoneNumberInvalidError, AuthRestartError, PhoneCodeExpiredError, PhoneCodeExpiredError
from collections import defaultdict
from client_wrapper import ClientWrapper
from config import Config

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

    try:
        await user_clients[phone_number].get_client().sign_in(phone_number, auth_code)
    except SessionPasswordNeededError:
        print("two-steps verification is active")
        return jsonify({"error": "two-steps verification is active"}), 401
    except PhoneCodeExpiredError:
        print("The confirmation code has expired")
        return jsonify({"error": "The confirmation code has expired"}), 400
    except PhoneCodeInvalidError:
        print("The phone code entered was invalid")
        return jsonify({"error": "The phone code entered was invalid"}), 400
    except Exception as e:
        print(f"Error in sign_in(): {str(e)}")
        return jsonify({"error": str(e)}), 500

    print(f"{phone_number} is logged in")
    # save user id in the session
    sender = await user_clients[phone_number].get_client().get_me()
    user_clients[phone_number].set_id(sender.id)

    count = 0
    res = defaultdict(int)

    try:
        if await user_clients[phone_number].get_client().is_user_authorized():
            dialogs = await user_clients[phone_number].get_client().get_dialogs()
            for dialog in dialogs:
                # TODO: check if chat was already sold
                if dialog.id < 0 or dialog.entity.bot == True or dialog.id == 777000:
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

    res_json_serializable = {str(key): value for key, value in res.items()}

    # Print the JSON-serializable dictionary
    print(res_json_serializable)
    return jsonify(res_json_serializable), 200


@login_route.route("/send-code", methods=["POST"])
async def send_code():
    data = await request.get_json()
    phone_number = data.get("phone_number")
    if phone_number is None:
        return jsonify({"error": "phone_number is missing"}), 400
    
    print(f"sending auth code to {phone_number}")

    if phone_number not in user_clients:
        # TODO: here we create a "user", but at this point the user is not logged on yet (confusing)
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

    return "ok", 200
