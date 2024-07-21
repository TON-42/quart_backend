from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is set
if not DATABASE_URL:
    logger.error("No DATABASE_URL found in environment variables")
    raise ValueError("No DATABASE_URL found in environment variables")

Base = declarative_base()


# Create engine and session in a function to avoid import-time side effects
def get_engine():
    try:
        return create_engine(DATABASE_URL)
    except SQLAlchemyError as e:
        logger.error(f"Error creating engine: {e}")
        raise


def create_sqlalchemy_sessionmaker():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize the database (create tables)
def init_db():
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        raise


# Context manager for database sessions
@asynccontextmanager
async def get_sqlalchemy_session():
    Session = create_sqlalchemy_sessionmaker()
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


# Function to create a persistent database session
def get_persistent_sqlalchemy_session():
    Session = create_sqlalchemy_sessionmaker()
    session = Session()
    return session
