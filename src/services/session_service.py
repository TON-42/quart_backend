from db import get_sqlalchemy_session, get_persistent_sqlalchemy_session
from models import User, Chat, Session, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import logging

logger = logging.getLogger(__name__)


async def create_sqlalchemy_session(client, number, phone_hash, userId):
    session_id = client.session.save()
    db_session = get_persistent_sqlalchemy_session()  # Use the persistent session
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
        logger.info(f"Creating new session for {number}({userId})")
    except Exception as e:
        db_session.rollback()  # Rollback in case of an error
        logger.error(f"Error creating new session: {str(e)}")
        exit_code = 1
    finally:
        db_session.close()  # Explicitly close the session if everything is fine
    return exit_code


# async def get_db_session(number, userId):
#     print(f"get_db_session: {number}, user_id: {userId}")
#     db_session = DBSession()
#     exit_code = 0
#     try:
#         if number is not None:
#             print("Trying to find a session with phone number")
#             found_session = (
#                 db_session.query(Session).filter(Session.phone_number == number).one()
#             )
#         else:
#             print("Trying to find a session with user_id")
#             found_session = (
#                 db_session.query(Session).filter(Session.user_id == str(userId)).one()
#             )
#         db_session.close()
#         return found_session
#     except NoResultFound:
#         print("session is not found :(")
#         db_session.close()
#         return None
#     except Exception as e:
#         print(f"Error while looking for a session: {str(e)}")
#         db_session.close()
#         return None


async def fetch_user_session(phone_number, user_id):
    logger.info(
        f"fetch_user_session - phone_number: {phone_number}, user_id: {user_id}"
    )
    db_session = get_persistent_sqlalchemy_session()
    try:
        if phone_number is not None:
            logger.info("Trying to find a session with phone number")
            found_session = (
                db_session.query(Session)
                .filter(Session.phone_number == phone_number)
                .one()
            )
        else:
            logger.info("Trying to find a session with user_id")
            found_session = (
                db_session.query(Session).filter(Session.user_id == str(user_id)).one()
            )
        return found_session
    except NoResultFound:
        logger.warning("Session not found")
        return None
    except Exception as e:
        logger.error(f"Error while looking for a session: {str(e)}")
        return None


async def delete_session(number, userId):
    async with get_sqlalchemy_session() as db_session:
        exit_code = 0
        try:
            if number is None:
                found_session = (
                    db_session.query(Session).filter(Session.user_id == userId).all()
                )
            else:
                found_session = (
                    db_session.query(Session)
                    .filter(Session.phone_number == number)
                    .all()
                )

            for one_session in found_session:
                db_session.delete(one_session)

            db_session.commit()
            return True
        except NoResultFound:
            logger.warning("Session in delete_session is not found")
            return False
        except Exception as e:
            logger.error(f"Error while deleting a session: {str(e)}")
            return False


async def set_session_is_logged_and_user_id(number, sender_id):
    async with get_sqlalchemy_session() as db_session:
        try:
            found_session = (
                db_session.query(Session).filter(Session.phone_number == number).one()
            )
            found_session.is_logged = True
            found_session.user_id = sender_id
            db_session.commit()
            return True
        except NoResultFound:
            logger.warning("Session not found in set_session_is_logged_and_user_id")
            return False
        except Exception as e:
            logger.error(f"Error in set_session_is_logged_and_user_id(): {str(e)}")
            return False


async def set_session_chats(number, all_chats):
    async with get_sqlalchemy_session() as db_session:
        try:
            found_session = (
                db_session.query(Session).filter(Session.phone_number == number).one()
            )
            found_session.chats = all_chats
            db_session.commit()
            return True
        except NoResultFound:
            logger.warning("Session not found in set_session_chats")
            return False
        except Exception as e:
            logger.error(f"Error in set_session_chats(): {str(e)}")
            return False
