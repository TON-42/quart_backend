from quart import Blueprint, jsonify, request
from shared import user_clients
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, AuthRestartError
from collections import defaultdict
from client_wrapper import ClientWrapper
from config import Config

login_route = Blueprint('login_route', __name__)

@login_route.route('/login', methods=['POST'])
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
                print(dialog)
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


@login_route.route("/send-code", methods=["POST"])
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

    user_clients[phone_number] = ClientWrapper(phone_number, Config.API_ID, Config.API_HASH)

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
