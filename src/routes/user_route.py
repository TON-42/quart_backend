from quart import Blueprint, jsonify, request
from db import get_sqlalchemy_session
from sqlalchemy.orm import joinedload
from models import User, Chat
from services.user_service import create_user
from services.user_service import manage_user_state
import logging
import os

logger = logging.getLogger(__name__)

DEBUG_MODE = os.getenv("DEBUG_MODE") == "True"

user_route = Blueprint("user_route", __name__)


def log_user_details(user, db_session, session_chats):
    logger.debug(
        f"Session still active after manage_user_state: {db_session.is_active}"
    )
    logger.debug(f"User name: {user.name}")
    logger.debug(f"User chats: {user.chats}")

    for chat in user.chats:
        logger.debug(f"Chat ID: {chat.id}, Chat name: {chat.name}")
        logger.debug(f"Chat users: {[user.id for user in chat.users]}")
        logger.debug(f"Chat lead: {chat.lead}")
        logger.debug(
            f"Chat agreed users: {[agreed_user.id for agreed_user in chat.agreed_users]}"
        )

    if not db_session.is_active:
        logger.debug("Session is not active!")
    else:
        logger.debug("Session is active!")

    logger.debug(f"User: {user}")
    logger.debug(f"User ID: {user.id}")
    logger.debug(f"User Name: {user.name}")
    logger.debug(f"User Has Profile: {user.has_profile}")
    logger.debug(f"User Words: {user.words}")
    logger.debug(f"User Registration Date: {user.registration_date}")
    logger.debug(f"User Auth Status: {user.auth_status}")
    logger.debug(f"Session Chats: {session_chats}")
    for chat in user.chats:
        logger.debug(f"Chat ID: {chat.id}")
        logger.debug(f"Chat Name: {chat.name}")
        logger.debug(f"Chat Words: {chat.words}")
        logger.debug(f"Chat Status: {chat.status.name}")
        if chat.lead:
            logger.debug(f"Chat Lead ID: {chat.lead.id}")
            logger.debug(f"Chat Lead Name: {chat.lead.name}")
        for agreed_user in chat.agreed_users:
            logger.debug(f"Agreed User ID: {agreed_user.id}")
        for user in chat.users:
            logger.debug(f"Chat User ID: {user.id}")


@user_route.route("/get-user", methods=["POST"])
async def get_user():
    try:
        if not request.is_json:
            return jsonify({"error": "Request data must be JSON"}), 400

        data = await request.get_json()
        username = data.get("username", "None")
        user_id = data.get("userId")

        if user_id is None:
            return jsonify({"error": "userId is missing"}), 400

        logger.info(f"get-user: {username}")
        logger.info(f"get-user: {user_id}")

        await create_user(user_id, username, False)

        async with get_sqlalchemy_session() as db_session:
            try:
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
                logger.debug(f"User loaded: {user}")
                logger.debug(f"User id: {user.id if user else 'User not found'}")
                logger.debug(f"User session: {db_session.is_active}")
                logger.debug(f"User instance state: {db_session.is_modified(user)}")

                auth_status_is_auth_code = False  # we have to save auth_code before it is overwritten with default
                if user.auth_status == "auth_code":
                    auth_status_is_auth_code = True

                session_chats = await manage_user_state(db_session, user, user_id)
                if session_chats == "error":
                    return jsonify({"error": "Error in looking for a session"}), 500

                if DEBUG_MODE:
                    log_user_details(user, db_session, session_chats)

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
                logger.info(f"Response: {response}")
                return jsonify(response), 200

            except Exception as e:
                logger.error(f"Error in fetching data from db: {str(e)}")
                return jsonify({"error": str(e)}), 500

    except Exception as e:
        logger.error(f"Error in /get-user: {str(e)}")
        return jsonify({"error": str(e)}), 500
