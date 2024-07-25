"""
Database utility functions and session management.
"""

import os
import logging
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL", "")

# Check if DATABASE_URL is set
if not DATABASE_URL:
    logger.error("No DATABASE_URL found in environment variables")
    raise ValueError("No DATABASE_URL found in environment variables")

Base = declarative_base()


def get_engine():
    """
    Creates and returns a SQLAlchemy engine using the DATABASE_URL from the environment.
    """
    try:
        return create_engine(DATABASE_URL)
    except SQLAlchemyError as e:
        logger.error("Error creating engine: %s", e)
        raise


def create_sessionmaker():
    """
    Creates and returns a sessionmaker object for SQLAlchemy sessions.
    """
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initializes the database by creating all defined tables.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error("Error creating engine: %s", e)
        raise


@asynccontextmanager
async def get_sqlalchemy_session():
    """
    Provides a SQLAlchemy session for asynchronous context management.
    """
    Session = create_sessionmaker()
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error("Session error: %s", e)
        session.rollback()
        raise
    finally:
        session.close()


def get_persistent_sqlalchemy_session():
    """
    Creates and returns a persistent SQLAlchemy session.
    """
    Session = create_sessionmaker()
    session = Session()
    return session
