# src/services/session_expiration.py

from datetime import datetime, timedelta
from config import Config
from db import get_sqlalchemy_session
from models import Session as SessionModel
from services.session_service import delete_session
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import asyncio
import logging

logger = logging.getLogger(__name__)


async def check_session_expiration():
    while True:
        async with get_sqlalchemy_session() as db_session:
            try:
                all_sessions = db_session.query(SessionModel).all()

                for user_session in all_sessions:
                    time_difference = datetime.now() - user_session.creation_date
                    if time_difference >= timedelta(
                        minutes=Config.SESSION_EXPIRATION_MINUTES
                    ):
                        logger.info(
                            f"Session for {user_session.phone_number} has expired."
                        )
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
                        logger.info(
                            f"Session for: {user_session.phone_number} is active"
                        )
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
        await asyncio.sleep(Config.CHECK_INTERVAL_SECONDS)
