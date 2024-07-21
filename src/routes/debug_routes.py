from quart import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from models import User, Chat, agreed_users_chats, users_chats
from models import Session as SessionModel
from db import create_sqlalchemy_sessionmaker, get_sqlalchemy_session

from bot import global_message

debug_routes = Blueprint("debug_routes", __name__)


@debug_routes.route("/send-global-message", methods=["POST"])
async def send_global_message():
    data = await request.get_json()

    message = data.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        async with get_sqlalchemy_session() as db_session:
            users = db_session.query(User).options(joinedload(User.chats)).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    await global_message(users, message)
    return "ok", 200


@debug_routes.route("/get-users", methods=["GET"])
async def get_users():
    try:
        # Use the get_sqlalchemy_session context manager
        async with get_sqlalchemy_session() as db_session:
            users = db_session.query(User).options(joinedload(User.chats)).all()
            users_json = [
                {
                    "id": user.id,
                    "name": user.name,
                    "has_profile": user.has_profile,
                    "words": user.words,
                    "chats": [chat.id for chat in user.chats],
                    "registration date": user.registration_date,
                    "auth_status": user.auth_status,
                }
                for user in users
            ]
            return jsonify(users_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@debug_routes.route("/get-chats", methods=["GET"])
async def get_chats():
    try:
        async with get_sqlalchemy_session() as db_session:
            chats = (
                db_session.query(Chat)
                .options(joinedload(Chat.agreed_users), joinedload(Chat.users))
                .all()
            )
            chats_json = [
                {
                    "id": chat.id,
                    "name": chat.name,
                    "words": chat.words,
                    "status": chat.status.name,  # Convert enum to string
                    "lead": chat.lead_id,
                    "telegram_id": chat.telegram_id,
                    "agreed_users": [user.id for user in chat.agreed_users],
                    "users": [user.id for user in chat.users],
                }
                for chat in chats
            ]
        return jsonify(chats_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@debug_routes.route("/get-sessions", methods=["GET"])
async def get_sessions():
    try:
        async with get_sqlalchemy_session() as db_session:
            sessions = db_session.query(SessionModel).all()
            sessions_json = [
                {
                    "id": session.id,
                    "phone_number": session.phone_number,
                    "user_id": session.user_id,
                    "created_at": session.creation_date,
                    "chats": session.chats,
                }
                for session in sessions
            ]
        return jsonify(sessions_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@debug_routes.route("/delete-session", methods=["POST"])
async def delete_one_session():
    data = await request.get_json()
    phone_number = data.get("phone_number")
    if phone_number is None:
        return jsonify({"error": "phone_number is missing"}), 400

    try:
        async with get_sqlalchemy_session() as db_session:
            try:
                found_session = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.phone_number == phone_number)
                    .first()
                )
                if found_session:
                    db_session.delete(found_session)
                    db_session.commit()
                    response = {"message": "Session has been deleted."}
                    status_code = 200
                else:
                    response = {"error": "No session found."}
                    status_code = 404
            except IntegrityError as e:
                db_session.rollback()
                response = {"error": f"Integrity error occurred: {str(e)}"}
                status_code = 500
    except Exception as e:
        response = {"error": f"An error occurred: {str(e)}"}
        status_code = 500

    return jsonify(response), status_code


@debug_routes.route("/delete-user", methods=["GET"])
async def delete_user():
    user_id = request.args.get("id", type=int)

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        async with get_sqlalchemy_session() as db_session:
            try:
                user = (
                    db_session.query(User)
                    .options(joinedload(User.chats).joinedload(Chat.users))
                    .filter(User.id == user_id)
                    .first()
                )

                if not user:
                    response = {"error": "No user found."}
                    status_code = 404
                else:
                    # Delete all connected chats
                    for chat in user.chats:
                        db_session.delete(chat)

                    # Delete the user
                    db_session.delete(user)
                    db_session.commit()

                    response = {"message": "User has been deleted."}
                    status_code = 200
            except IntegrityError as e:
                db_session.rollback()
                response = {"error": f"Integrity error occurred: {str(e)}"}
                status_code = 500
    except Exception as e:
        response = {"error": f"An error occurred: {str(e)}"}
        status_code = 500

    return jsonify(response), status_code


@debug_routes.route("/delete-chat", methods=["GET"])
async def delete_chat():
    chat_id = request.args.get("id", type=int)

    if not chat_id:
        return jsonify({"error": "Chat ID is required"}), 400

    try:
        async with get_sqlalchemy_session() as db_session:
            try:
                chat = db_session.query(Chat).filter(Chat.id == chat_id).one()

                if not chat:
                    response = {"error": "No chat found."}
                    status_code = 404
                else:
                    # Delete the chat
                    db_session.delete(chat)
                    db_session.commit()

                    response = {"message": "Chat has been deleted."}
                    status_code = 200
            except NoResultFound:
                response = {"error": "No chat found."}
                status_code = 404
            except IntegrityError as e:
                db_session.rollback()
                response = {"error": f"Integrity error occurred: {str(e)}"}
                status_code = 500
    except Exception as e:
        response = {"error": f"An error occurred: {str(e)}"}
        status_code = 500

    return jsonify(response), status_code


# @debug_routes.route("/delete-all-chats", methods=["GET"])
# async def delete_chats():
#     try:
#         # Create a session
#         session = Session()

#         try:
#             session.query(agreed_users_chats).delete()
#             session.query(users_chats).delete()
#             session.query(Chat).delete()
#             session.commit()

#             response = {"message": f"Chats have been deleted."}
#             status_code = 200

#         except IntegrityError as e:
#             session.rollback()
#             response = {"error": f"Integrity error occurred: {str(e)}"}
#             status_code = 500

#     except Exception as e:
#         session.rollback()
#         response = {"error": f"An error occurred: {str(e)}"}
#         status_code = 500

#     finally:
#         session.close()

#     return jsonify(response), status_code

# @debug_routes.route("/delete-all-users", methods=["GET"])
# async def delete_users():
#     try:
#         # Create a session
#         session = Session()

#         try:
#             session.query(agreed_users_chats).delete()
#             session.query(users_chats).delete()
#             session.query(User).delete()
#             session.commit()

#             response = {"message": f"Users have been deleted."}
#             status_code = 200

#         except IntegrityError as e:
#             session.rollback()
#             response = {"error": f"Integrity error occurred: {str(e)}"}
#             status_code = 500

#     except Exception as e:
#         session.rollback()
#         response = {"error": f"An error occurred: {str(e)}"}
#         status_code = 500

#     finally:
#         session.close()

#     return jsonify(response), status_code

# ------------------ DEBUG routes ---------------------------

# @app.route('/send', methods=['GET'])
# async def send():
#     API_URL = "http://localhost:8080/access"

#     # Data to send in the request body (as JSON)
#     data = {"username": API_USERNAME, "password": API_PASSWORD}

#     # Send POST request with JSON data
#     async with httpx.AsyncClient() as client:
#         response = await client.post(API_URL, json=data)

#     print(response)
#     # Check for successful response
#     if response.status_code == 200:
#         # Access token is in the response data
#         access_token = response.json().get("access_token")
#         return "ok", 200
#     else:
#         # Handle error
#         return "ko", response.status_code

# @debug_routes.route('/send', methods=['GET'])
# async def request_hello():
#     send_url = "http://localhost:8080/access"
#     hello_url = "http://localhost:8080/hello"
#     data = {"username": API_USERNAME, "password": API_PASSWORD}
#     async with httpx.AsyncClient() as client:
#         # Get the JWT token from the /send endpoint
#         response = await client.post(send_url, json=data)
#         if response.status_code == 200:
#             access_token = response.json().get("access_token")
#             headers = {
#                 "Authorization": f"Bearer {access_token}"
#             }

#             # Use the token to access the /hello endpoint
#             hello_response = await client.get(hello_url, headers=headers)
#             if hello_response.status_code == 200:
#                 print(hello_response.json())
#                 return jsonify([hello_response.json(), response.json()])
#             else:
#                 print(f"Failed to access /hello: {hello_response.status_code}")
#         else:
#             print(f"Failed to get token: {send_response.status_code}")
#     return "ko", 500

# @debug_routes.route("/create-user", methods=["GET"])
# async def create_test_user():
#     session = Session()
#     status = 0
#     response = jsonify({"message": "OK"}), 200
#     try:
#         await client.get_dialogs()

#         user_entity = await client.get_entity(int(user_id))

#         if user_entity.username:
#             return user_entity.username
#         else:
#             return False
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({f"Error: {str(e)}"}), 400
#     try:
#         # Query the database to check if a user with the provided ID exists
#         existing_user = session.query(User).filter(User.id == 3243252343).one()
#         print("User already exists")
#     except NoResultFound:
#         new_user = User(id=3243252343, name="dantollllll", has_profile=False, words=0)
#         user_data = {
#             "id": new_user.id,
#             "name": new_user.name,
#             "has_profile": new_user.has_profile,
#             "words": new_user.words
#         }

#         print(user_data)
#         session.add(new_user)
#         session.commit()
#         response =  jsonify(user_data), 200
#         print("added")
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         response = jsonify({f"Error: {str(e)}"}), 400
#     finally:
#         session.close()
#     return response

# @debug_routes.route("/create-chat", methods=["GET"])
# async def create_chat():
#     # Enum for chat status
#     status = 0
#     try:
#         session = Session()

#         new_chat = Chat(id=32432525, name="Ton_stuff", words=12345, status=ChatStatus.pending, lead_id=32432524, full_text="123")

#         lead = session.query(User).filter(User.id == 32432524).one()
#         new_chat.lead = lead

#         agreed_user_ids = [32432524]
#         agreed_users = session.query(User).filter(User.id.in_(agreed_user_ids)).all()
#         new_chat.agreed_users.extend(agreed_users)

#         all_users = session.query(User).filter(User.id.in_([32432524, 32432525])).all()
#     new_chat.users.extend(all_users)

#     session.add(new_chat)
#     session.commit()
# except Exception as e:
#     print(f"Error: {str(e)}")
#     return jsonify({f"Error: {str(e)}"}), 400
#     status = 1
# finally:
#     session.close()
#     return jsonify({"message": "OK"}), 200
# return status


# -----------------------------------------------
