from db import Session as DBSession
from models import User, Chat, Session as SessionModel
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from config import Config
from utils import connect_client


async def create_user(user_id, username, profile):
    db_session = DBSession()
    try:
        existing_user = db_session.query(User).filter(User.id == user_id).one()
    except NoResultFound:
        if username is None:
            username = "Unknown"
        new_user = User(
            id=user_id,
            name=username,
            has_profile=profile,
            words=0,
            auth_status="default",
            id=user_id,
            name=username,
            has_profile=profile,
            words=0,
            auth_status="default",
        )
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "has_profile": new_user.has_profile,
            "words": new_user.words,
            "auth_status": new_user.auth_status,
            "auth_status": new_user.auth_status,
        }

        print(f"new user created: {user_data}")
        db_session.add(new_user)
        db_session.commit()
    except Exception as e:
        print(f"Error creating a user: {str(e)}")
    finally:
        db_session.close()


async def set_has_profile(user_id, has_profile):
    db_session = DBSession()
    status = 0
    try:
        user = db_session.query(User).filter(User.id == user_id).one()
        user.has_profile = has_profile
        db_session.commit()
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        status = 1
    finally:
        db_session.close()
        return status


async def set_auth_status(user_id, status):
    db_session = DBSession()
    exit_code = 0
    try:
        user = db_session.query(User).filter(User.id == user_id).one()
        user.auth_status = status
        db_session.commit()
        print(f"auth_status => {user.auth_status}")
    except Exception as e:
        print(f"Error updating auth_status: {str(e)}")
        exit_code = 1
    finally:
        db_session.close()
        return exit_code


async def get_user_chats(sender_id, sender_name):
    db_session = DBSession()
    chat_ids = []
    try:
        user = (
            db_session.query(User)
            .options(joinedload(User.chats).joinedload(Chat.users))
            .filter(User.id == sender_id)
            .first()
        )

        chat_ids = [chat.id for chat in user.chats]
        print(f"User {sender_name} previously sold chats: {chat_ids}")
        db_session.close()
        return chat_ids
    except Exception as e:
        print(f"Error in get_user_chats(): {str(e)}")
        db_session.close()
        return 1


async def manage_user_state(db_session, user, user_id):
    is_logged_in = False
    chats = None
    try:
        user_session = (
            session.query(MySession).filter(MySession.user_id == str(user_id)).first()
        )
        user_session = (
            db_session.query(SessionModel)
            .filter(SessionModel.user_id == str(user_id))
            .first()
        )
        # if session exists and user is logged in => double check logged in status
        if user_session and user_session.is_logged:
            client = TelegramClient(
                StringSession(user_session.id), Config.API_ID, Config.API_HASH
            )
            client = TelegramClient(
                StringSession(user_session.id), Config.API_ID, Config.API_HASH
            )
            if await connect_client(client, None, user_id) == -1:
                print("error in connecting to Telegram")
                return jsonify({"error": "error in connecting to Telegram"}), 500
            # get session chats
            chats = user_session.chats
            if await client.is_user_authorized():
                print(f"{user.name} is logged in")
                is_logged_in = True
            await client.disconnect()
        # if user is not logged in => change status back to default
        if is_logged_in == False and user.auth_status != "default":
            print("auth_status => default")
            user.auth_status = "default"
            db_session.commit()
            # change auth_code to default but return auth_code to show pin code once
            if user.auth_status == "auth_code":
                user.auth_status = "auth_code"
    except NoResultFound:
        print(f"{user.name} session does not exist")
    except Exception as e:
        db_session.close()
        print(f"error in looking for a session: {str(e)}")
        return "error"
        return "error"
    return chats
