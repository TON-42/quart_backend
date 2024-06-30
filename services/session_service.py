from db import Session as S
from models import User, Chat, Session, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import os

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
async def create_session(client, number, phone_hash):
    session_id = client.session.save()
    session = S()
    exit_code = 0
    try:
        new_session = Session(id=session_id, phone_number=number, phone_code_hash=phone_hash)
        session.add(new_session)
        session.commit()
        print(f"Creating new session")
    except Exception as e:
        print(f"Error creating new session: {str(e)}")
        exit_code = 1
    finally:
        session.close()
        return exit_code

async def session_exists(number):
    session = S()
    exit_code = 0
    try:
        found_session = session.query(Session).filter(Session.phone_number == number).one()
        return found_session
    except NoResultFound:
        session.close()
        return None
    except Exception as e:
        print(f"Error while looking for a session: {str(e)}")
        session.close()
        return None

async def delete_session(number):
    session = S()
    exit_code = 0
    try:
        found_session = session.query(Session).filter(Session.phone_number == number).one()

        session.delete(found_session)
        session.commit()
        session.close()
        return True
    except NoResultFound:
        print("Session in delete_session is not found")
        session.close()
        return False
    except Exception as e:
        print(f"Error while looking for a session: {str(e)}")
        session.close()
        return False