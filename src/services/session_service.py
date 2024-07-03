from db import Session as S
from models import User, Chat, Session, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import os

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
async def create_session(client, number, phone_hash, userId):
    session_id = client.session.save()
    session = S()
    exit_code = 0
    try:
        if userId is None:
            userId = "None"
        new_session = Session(id=session_id, phone_number=number, phone_code_hash=phone_hash, user_id=userId)
        session.add(new_session)
        session.commit()
        print(f"Creating new session")
    except Exception as e:
        print(f"Error creating new session: {str(e)}")
        exit_code = 1
    finally:
        session.close()
        return exit_code

async def session_exists(number, userId):
    print(f"inside session_exists: {number}, user_id: {userId}")
    session = S()
    exit_code = 0
    try:
        if userId is not None:
            print("Trying to find a session with user_id")
            found_session = session.query(Session).filter(Session.user_id == str(userId)).one()
        else:    
            found_session = session.query(Session).filter(Session.phone_number == number).one()
        session.close()
        return found_session
    except NoResultFound:
        print("session is not found :(")
        session.close()
        return None
    except Exception as e:
        print(f"Error while looking for a session: {str(e)}")
        session.close()
        return None

async def delete_session(number, userId):
    session = S()
    exit_code = 0
    try:
        if number is None:
            found_session = session.query(Session).filter(Session.user_id == userId).all()
        else:
            found_session = session.query(Session).filter(Session.phone_number == number).all()

        for one_session in found_session:
            session.delete(one_session)
    
        session.commit()
        session.close()
        return True
    except NoResultFound:
        print("Session in delete_session is not found")
        session.close()
        return False
    except Exception as e:
        print(f"Error while deleting for a session: {str(e)}")
        session.close()
        return False

async def set_session_is_logged_and_user_id(number, sender_id):
    session = S()
    exit_code = 0
    try:
        found_session = session.query(Session).filter(Session.phone_number == number).one()
        found_session.is_logged = True
        found_session.user_id = sender_id
        session.commit()
        session.close()
        return True
    except NoResultFound:
        session.close()
        return False
    except Exception as e:
        print(f"Error setting is logged in session: {str(e)}")
        session.close()
        return False

async def set_session_chats(number, all_chats):
    session = S()
    exit_code = 0
    try:
        found_session = session.query(Session).filter(Session.phone_number == number).one()
        found_session.chats = all_chats
        session.commit()
        session.close()
        return True
    except NoResultFound:
        session.close()
        return False
    except Exception as e:
        print(f"Error saving chats in session: {str(e)}")
        session.close()
        return False
