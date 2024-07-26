"""
Routes for user related operations
"""

import os
import logging
from sqlalchemy.orm import joinedload
from quart import Blueprint, jsonify, request
from db import get_sqlalchemy_session
from models import User, Chat
from services.user_service import create_user
from services.user_service import manage_user_state

logger = logging.getLogger(__name__)

DEBUG_MODE = os.getenv("DEBUG_MODE") == "True"

user_route = Blueprint("user_route", __name__)


def log_user_details(user, db_session, session_chats):
    """
    Get user details
    """
    logger.debug(
        "Session still active after manage_user_state: %s", db_session.is_active
    )
    logger.debug("User name: %s", user.name)
    logger.debug("User chats: %s", user.chats)
    for chat in user.chats:
        logger.debug("chat id: %s, chat name: %s", chat.id, chat.name)
        logger.debug("chat users: %s", [user.id for user in chat.users])
        logger.debug("chat lead: %s", chat.lead)
        logger.debug(
            "chat agreed users: %s",
            [agreed_user.id for agreed_user in chat.agreed_users],
        )
    if not db_session.is_active:
        logger.debug("Session is not active!")
    else:
        logger.debug("Session is active!")

    logger.debug("User: %s", user)
    logger.debug("User ID: %s", user.id)
    logger.debug("User Name: %s", user.name)
    logger.debug("User Has Profile: %s", user.has_profile)
    logger.debug("User Words: %s", user.words)
    logger.debug("User Registration Date: %s", user.registration_date)
    logger.debug("User Auth Status: %s", user.auth_status)
    logger.debug("Session Chats: %s", session_chats)
    for chat in user.chats:
        logger.debug("Chat ID: %s", chat.id)
        logger.debug("Chat Name: %s", chat.name)
        logger.debug("Chat Words: %s", chat.words)
        logger.debug("Chat Status: %s", chat.status.name)
        if chat.lead:
            logger.debug("Chat Lead ID: %s", chat.lead.id)
            logger.debug("Chat Lead Name: %s", chat.lead.name)
        for agreed_user in chat.agreed_users:
            logger.debug("Agreed User ID: %s", agreed_user.id)
        for user in chat.users:
            logger.debug("Chat User ID: %s", user.id)


@user_route.route("/get-user", methods=["POST"])
async def get_user():
    """
    Get user data from the database
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request data must be JSON"}), 400

        data = await request.get_json()
        username = data.get("username", "None")
        user_id = data.get("userId")

        if user_id is None:
            return jsonify({"error": "userId is missing"}), 400

        logger.info("username: %s", username)
        logger.info("user id: %s", user_id)

        await create_user(user_id, username, False)

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
            logger.debug("User loaded: %s", user)
            logger.debug("User id: %s", user.id if user else "User not found")
            logger.debug("User session: %s", db_session.is_active)
            logger.debug("User instance state: %s", db_session.is_modified(user))
            if user is None:
                return jsonify({"error": "User not found"}), 404

            auth_status_is_auth_code = bool(user.auth_status == "auth_code")

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
            print(f"Response: {response}")
            return jsonify(response), 200

    except Exception as e:
        logger.error("Error in /get-user: %s", str(e))
        return jsonify({"error": str(e)}), 500
