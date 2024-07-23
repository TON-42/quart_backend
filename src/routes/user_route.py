from quart import Blueprint, jsonify, request
from db import Session
from sqlalchemy.orm import joinedload
from models import User, Chat, Quest
from models import Session as MySession
from services.user_service import create_user
from sqlalchemy.orm.exc import NoResultFound
from utils import get_chat_id, count_words, connect_client
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from config import Config
from services.user_service import manage_user_state

user_route = Blueprint("user_route", __name__)

@user_route.route("/quests", methods=["POST"])
async def quests():
    try:
        session = Session()
        data = await request.get_json()
        points = data.get("points", 0)
        user_id = data.get("user_id")
        quest_data = data.get("data")
        title = data.get("title")

        try:
            existing_quest = session.query(Quest).filter(Quest.user_id == user_id, Quest.name == title).one()
            print(f"Quest {title} already exists")
            return jsonify({"error": "Quest already exists"}), 400
        except NoResultFound:
            print(f"Creating new quest {title}")

        try:
            user = (
                session.query(User)
                .options(joinedload(User.chats))
                .filter(User.id == user_id)
                .one()
            )
            new_quest = Quest(
                name=title,
                data=quest_data,
                user_id=user_id,
            )
        except Exception as e:
            print(f"Error in retrieving user from db: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
        user.words += points
        session.add(new_quest)
        session.commit()
        session.close()
        return jsonify({"message": "ok"}), 200
    except Exception as e:
        print(f"Error in /quests: {str(e)}")
        return jsonify({"error": str(e)}), 500

@user_route.route("/get-quests", methods=["GET"])
async def get_quests():
    try:
        session = Session()

        quests = session.query(Quest).all()

        session.close()

        quests_json = [
            {
                "id": quest.id,
                "name": quest.name,
                "user_id": quest.user_id,
                "data": quest.data
            }
            for quest in quests
        ]

        return jsonify(quests_json)

    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500


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

        print(f"get-user: {username}")

        try:
            await create_user(user_id, username, False)
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return jsonify({"error": str(e)}), 500
        try:
            session = Session()

            user = (
                session.query(User)
                .options(
                    joinedload(User.chats).joinedload(Chat.users),
                    joinedload(User.chats).joinedload(Chat.lead),
                    joinedload(User.chats).joinedload(Chat.agreed_users),
                )
                .filter(User.id == user_id)
                .first()
            )

            auth_code = (
                False  # we have to save auth_code before it is overwritten with default
            )
            if user.auth_status == "auth_code":
                auth_code = True

            session_chats = None
            session_chats = await manage_user_state(session, user, user_id)
            if session_chats == "error":
                return jsonify({"error in looking for a session"}), 500

        except Exception as e:
            session.close()
            print(f"error in fetching data from db: {str(e)}")
            return jsonify({"error": str(e)}), 500

        response = {
            "id": user.id,
            "name": user.name,
            "has_profile": user.has_profile,
            "words": user.words,
            "registration_date": user.registration_date,
            "auth_status": "auth_code" if auth_code else user.auth_status,
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
        session.close()
        return jsonify(response), 200

    except Exception as e:
        print(f"error in /get-user: {str(e)}")
        return jsonify({"error": str(e)}), 500
