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

                auth_code = False  # we have to save auth_code before it is overwritten with default
                auth_status_is_auth_code = False  # we have to save auth_code before it is overwritten with default
                if user.auth_status == "auth_code":
                    auth_code = True
                    auth_status_is_auth_code = True

                session_chats = await manage_user_state(db_session, user, user_id)
                if session_chats == "error":
                    return jsonify({"error": "Error in looking for a session"}), 500

        except Exception as e:
            logger.error(f"Error in fetching data from db: {str(e)}")
            return jsonify({"error": str(e)}), 500

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
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in /get-user: {str(e)}")
        return jsonify({"error": str(e)}), 500
