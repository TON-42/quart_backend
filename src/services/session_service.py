from db import Session as DBSession
from models import User, Chat, Session, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from telethon.sessions import StringSession
from telethon.sync import TelegramClient


async def create_session(client, number, phone_hash, userId):
    session_id = client.session.save()
    db_session = DBSession()
    exit_code = 0
    try:
        if userId is None:
            userId = "None"
        new_session = Session(
            id=session_id,
            phone_number=number,
            phone_code_hash=phone_hash,
            user_id=userId,
        )
        db_session.add(new_session)
        db_session.commit()
        print(f"Creating new session for {number}({userId})")
    except Exception as e:
        print(f"Error creating new session: {str(e)}")
        exit_code = 1
    finally:
        session.close()
        return exit_code


async def session_exists(number, userId):
    print(f"session_exists: {number}, user_id: {userId}")
    db_session = DBSession()
    exit_code = 0
    try:
        if number is not None:
            print("Trying to find a session with phone number")
            found_session = (
                db_session.query(Session).filter(Session.phone_number == number).one()
            )
        else:
            print("Trying to find a session with user_id")
            found_session = (
                db_session.query(Session).filter(Session.user_id == str(userId)).one()
            )
        db_session.close()
        return found_session
    except NoResultFound:
        print("session is not found :(")
        db_session.close()
        return None
    except Exception as e:
        print(f"Error while looking for a session: {str(e)}")
        db_session.close()
        return None


async def delete_session(number, userId):
    db_session = DBSession()
    exit_code = 0
    try:
        if number is None:
            found_session = (
                db_session.query(Session).filter(Session.user_id == userId).all()
            )
        else:
            found_session = (
                db_session.query(Session).filter(Session.phone_number == number).all()
            )

        for one_session in found_session:
            db_session.delete(one_session)

        db_session.commit()
        db_session.close()
        return True
    except NoResultFound:
        print("Session in delete_session is not found")
        db_session.close()
        return False
    except Exception as e:
        print(f"Error while deleting for a session: {str(e)}")
        db_session.close()
        return False


async def set_session_is_logged_and_user_id(number, sender_id):
    db_session = DBSession()
    exit_code = 0
    try:
        found_session = (
            db_session.query(Session).filter(Session.phone_number == number).one()
        )
        found_session.is_logged = True
        found_session.user_id = sender_id
        db_session.commit()
        db_session.close()
        return True
    except NoResultFound:
        db_session.close()
        return False
    except Exception as e:
        print(f"Error in set_session_is_logged_and_user_id(): {str(e)}")
        db_session.close()
        return False


async def set_session_chats(number, all_chats):
    db_session = DBSession()
    exit_code = 0
    try:
        found_session = (
            db_session.query(Session).filter(Session.phone_number == number).one()
        )
        found_session.chats = all_chats
        db_session.commit()
        db_session.close()
        return True
    except NoResultFound:
        db_session.close()
        return False
    except Exception as e:
        print(f"Error in set_session_chats(): {str(e)}")
        db_session.close()
        return False
