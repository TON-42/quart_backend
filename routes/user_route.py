from quart import Blueprint, jsonify, request
from db import Session
from sqlalchemy.orm import joinedload
from models import User, Chat
from services.user_service import create_user

user_route = Blueprint('user_route', __name__)

@user_route.route("/get-user", methods=["POST"])
async def get_user():
    try:
        # Check if request is JSON
        if not request.is_json:
            return jsonify({"error": "Request data must be JSON"}), 400

        data = await request.get_json()
        username = data.get("username", "None")
        user_id = data.get("userId")

        if user_id is None:
            # TODO: what if user entered from browser(maybe add tmp user_id)
            return jsonify({"error": "userId is missing"}), 400
        
        print(f"get-user: {username}")
        
        try:
            await create_user(user_id, username, False)
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return jsonify({"error": "Internal error"}), 500
        try:
            session = Session()
            
            user = (
                session.query(User)
                .options(
                    joinedload(User.chats).joinedload(Chat.users),
                    joinedload(User.chats).joinedload(Chat.lead),
                    joinedload(User.chats).joinedload(Chat.agreed_users)
                )
                .filter(User.id == user_id)
                .first()
            )

            if user is None:
                session.close()
                return jsonify({"message": f"User with id {user_id} does not exist"}), 404

            for chat in user.chats:
                chat.agreed_users
            
        except Exception as e:
            session.close()
            return jsonify({"error": str(e)}), 500

        session.close()

        return jsonify(
            {
                "id": user.id,
                "name": user.name,
                "has_profile": user.has_profile,
                "words": user.words,
                "registration_date": user.registration_date,
                "auth_status": user.auth_status,
                "chats": [
                    {
                        "id": chat.id,
                        "name": chat.name,
                        "words": chat.words,
                        "status": chat.status.name,
                        "lead": {
                            "id": chat.lead.id,
                            "name": chat.lead.name
                        } if chat.lead else None,
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
        return jsonify({"error": str(e)}), 500
    
# @user_route.route("/is-active", methods=["POST"])
# async def is_active():
#     try:
#         data = await request.get_json()
#         user_id = data.get("userId")
        
#         if user_id is None:
#             return jsonify({"error": "userId is missing"}), 400

#         for phone_number, client_wrapper in user_clients.items():
#             if user_id == client_wrapper.get_id():
#                 return "ok", 200
#         return "Not found", 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500