# src/services/session_expiration.py

from datetime import datetime, timedelta, timezone
from config import Config
from db import get_persistent_sqlalchemy_session
from models import Session as SessionModel
from services.session_service import delete_session
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import asyncio
import logging

logger = logging.getLogger(__name__)


async def check_session_expiration():
    while True:
        db_session = get_persistent_sqlalchemy_session()
        try:
            all_sessions = db_session.query(SessionModel).all()

            for user_session in all_sessions:
                # creation_time = user_session.creation_date
                creation_time = user_session.creation_date.replace(tzinfo=timezone.utc)
                # current_time = datetime.now()
                current_time = datetime.now(timezone.utc)
                time_difference = current_time - creation_time
                logger.info(
                    f"Checking session for {user_session.phone_number}: "
                    f"Creation Time: {creation_time}, Current Time: {current_time}, "
                    f"Time Difference: {time_difference}, Expiry Threshold: "
                    f"{timedelta(minutes=Config.SESSION_EXPIRATION_MINUTES)}"
                )
                if time_difference >= timedelta(
                    minutes=Config.SESSION_EXPIRATION_MINUTES
                ):
                    logger.info(f"Session for {user_session.phone_number} has expired.")
                    if user_session.is_logged:
                        try:
                            client = TelegramClient(
                                StringSession(user_session.id),
                                Config.API_ID,
                                Config.API_HASH,
                            )
                            await client.connect()
                            if await client.is_user_authorized():
                                await client.log_out()
                        except Exception as e:
                            logger.error(f"Error in log_out(): {str(e)}")
                        finally:
                            await client.disconnect()
                    await delete_session(user_session.phone_number, None)
                else:
                    logger.info(f"Session for: {user_session.phone_number} is active")
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
        finally:
            db_session.close()
        logger.info(f"Sleeping for {Config.CHECK_INTERVAL_SECONDS} seconds")
        await asyncio.sleep(Config.CHECK_INTERVAL_SECONDS)
