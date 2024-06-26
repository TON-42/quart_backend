from db import Session
from models import User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from models import User, Chat, agreed_users_chats, users_chats


async def create_user(user_id, username, profile):
    session = Session()
    try:
        # Query the database to check if a user with the provided ID exists
        existing_user = session.query(User).filter(User.id == user_id).one()
        # print("User already exists")
    except NoResultFound:
        if username is None:
            username = "Unknown"
        new_user = User(
            id=user_id, name=username, has_profile=profile, words=0, auth_status="default"
        )
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "has_profile": new_user.has_profile,
            "words": new_user.words,
            "auth_status": new_user.auth_status
        }

        print(user_data)
        session.add(new_user)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        session.close()

async def set_has_profile(user_id, has_profile):
    session = Session()
    status = 0
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.has_profile = has_profile
        session.commit()
    except Exception as e:
        print(f"Error updating username or profile: {str(e)}")
        status = 1
    finally:
        session.close()
        return status

async def set_auth_status(user_id, status):
    session = Session()
    exit_code = 0
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.auth_status = status
        session.commit()
        print(f"Updating auth_status to {user.auth_status}")
    except Exception as e:
        print(f"Error updating auth_status: {str(e)}")
        exit_code = 1
    finally:
        session.close()
        return exit_code

async def get_user_chats(sender_id, sender_name):
    session = Session()
    chat_ids = []
    try:
        user = (
            session.query(User)
            .options(joinedload(User.chats).joinedload(Chat.users))
            .filter(User.id == sender_id)
            .first()
        )
        
        chat_ids = [chat.id for chat in user.chats]
        print(f"User {sender_name} previously sold chats: {chat_ids}")
        session.close()
        return chat_ids
    except Exception as e:
        print(f"Error before sign_in() {str(e)}")
        session.close()
        return 1