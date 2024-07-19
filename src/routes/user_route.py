from quart import Blueprint, jsonify, request
from db import get_sqlalchemy_session
from sqlalchemy.orm import joinedload
from models import User, Chat
from services.user_service import create_user
from services.user_service import manage_user_state
import logging

logger = logging.getLogger(__name__)

user_route = Blueprint("user_route", __name__)


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
            return jsonify({"error": "userId is missing"}), 400

        logger.info(f"get-user: {username}")

        try:
            await create_user(user_id, username, False)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return jsonify({"error": str(e)}), 500

        try:
            async with get_sqlalchemy_session() as db_session:
                user = (
                    db_session.query(User)
                    .options(
                        joinedload(User.chats).joinedload(Chat.users),
                        joinedload(User.chats).joinedload(Chat.lead),
                        joinedload(User.chats).joinedload(Chat.agreed_users),
                    )
                    .filter(User.id == user_id)
                    .first()
                )

                # Print statement to check if user is loaded and session status
                print(f"User loaded: {user}")
                print(f"User id: {user.id if user else 'User not found'}")
                print(f"User session: {db_session.is_active}")

                # Check if user instance is still in session
                print(f"User instance state: {db_session.is_modified(user)}")

                auth_code = False  # we have to save auth_code before it is overwritten with default
                auth_status_is_auth_code = False  # we have to save auth_code before it is overwritten with default
                if user.auth_status == "auth_code":
                    auth_code = True
                    auth_status_is_auth_code = True

                session_chats = await manage_user_state(db_session, user, user_id)
                if session_chats == "error":
                    return jsonify({"error": "Error in looking for a session"}), 500

                # Print statement to check if session is still active after manage_user_state
                print(
                    f"Session still active after manage_user_state: {db_session.is_active}"
                )
                # Attempt to access an attribute to see if it's still attached
                print(f"User name: {user.name}")
                print(f"User chats: {user.chats}")

                # Additional print statements
                for chat in user.chats:
                    print(f"Chat ID: {chat.id}, Chat name: {chat.name}")
                    print(f"Chat users: {[user.id for user in chat.users]}")
                    print(f"Chat lead: {chat.lead}")
                    print(
                        f"Chat agreed users: {[agreed_user.id for agreed_user in chat.agreed_users]}"
                    )

                # Additional checks
                if not db_session.is_active:
                    print("Session is not active!")
                else:
                    print("Session is active!")

        except Exception as e:
            logger.error(f"Error in fetching data from db: {str(e)}")
            return jsonify({"error": str(e)}), 500
        print("just before response")
        # Print statements before constructing the response
        print(f"User: {user}")
        print(f"User ID: {user.id}")
        print(f"User Name: {user.name}")
        print(f"User Has Profile: {user.has_profile}")
        print(f"User Words: {user.words}")
        print(f"User Registration Date: {user.registration_date}")
        print(f"User Auth Status: {user.auth_status}")
        print(f"Session Chats: {session_chats}")
        for chat in user.chats:
            print(f"Chat ID: {chat.id}")
            print(f"Chat Name: {chat.name}")
            print(f"Chat Words: {chat.words}")
            print(f"Chat Status: {chat.status.name}")
            if chat.lead:
                print(f"Chat Lead ID: {chat.lead.id}")
                print(f"Chat Lead Name: {chat.lead.name}")
            for agreed_user in chat.agreed_users:
                print(f"Agreed User ID: {agreed_user.id}")
            for user in chat.users:
                print(f"Chat User ID: {user.id}")

        response = {
            "id": user.id,
            "name": user.name,
            "has_profile": user.has_profile,
            "words": user.words,
            "registration_date": user.registration_date,
            "auth_status": (
                "auth_code" if auth_status_is_auth_code else user.auth_status
            ),
            "session_chats": session_chats,
            "chats": [
                {
                    "id": chat.id,
                    "name": chat.name,
                    "words": chat.words,
                    "status": chat.status.name,
                    "lead": (
                        {"id": chat.lead.id, "name": chat.lead.name}
                        if chat.lead
                        else None
                    ),
                    "agreed_users": [
                        agreed_user.id for agreed_user in chat.agreed_users
                    ],
                    "users": [user.id for user in chat.users],
                }
                for chat in user.chats
            ],
        }
        print(f"Response: {response}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in /get-user: {str(e)}")
        return jsonify({"error": str(e)}), 500
