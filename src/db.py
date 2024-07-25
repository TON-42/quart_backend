"""
Database utility functions and session management.
"""

import logging
import subprocess
import re
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from config import Config

load_dotenv()

logger = logging.getLogger(__name__)


DATABASE_URL = Config.DATABASE_URL
print(f"DATABASE_URL: {DATABASE_URL}")


# Function to ping the database host (for debug purposes)
def ping_database_host(host):
    """
    Pings the database host to check if it is reachable.
    """
    response = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True)
    print(response.stdout)


# Extract the host part from the DATABASE_URL for pinging
host_match = re.search(r"@([^:/]+)", DATABASE_URL)
if host_match:
    db_host = host_match.group(1)
    print(f"Pinging host: {db_host}")
    ping_database_host(db_host)
else:
    print("Host not found in DATABASE_URL")


# Extract the host from the DATABASE_URL
# host_match = re.search(r"@([^:]+)", DATABASE_URL)
# if host_match:
#     host = host_match.group(1)
#     print(f"Pinging host: {host}")
#     try:
#         response = subprocess.run(
#             ["ping", "-c", "4", host], capture_output=True, text=True
#         )
#         print(response.stdout)
#     except Exception as e:
#         print(f"Ping error: {e}")
# else:
#     print("Host not found in DATABASE_URL")

Base = declarative_base()


# Create SQLAlchemy engine
# engine = create_engine(DATABASE_URL)
# Create SQLAlchemy engine
def get_engine():
    """
    Creates and returns a SQLAlchemy engine using the DATABASE_URL from the environment.
    """
    try:
        print(f"Creating engine with URL: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        print("Engine created successfully.")
        return engine
    except SQLAlchemyError as e:
        logger.error("Error creating engine: %s", e)
        print(f"Error creating engine: {e}")
        raise


# try:
#     engine = create_engine(DATABASE_URL)
#     print("SQLAlchemy engine created successfully.")
# except SQLAlchemyError as e:
#     logger.error("Error creating engine: %s", e)
#     print(f"Error creating engine: {e}")

# Create session maker bound to the engine
# Session = sessionmaker(bind=engine)
# Create session maker bound to the engine
try:
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    print("Session maker created successfully.")
except SQLAlchemyError as e:
    logger.error("Error creating session maker: %s", e)
    print(f"Error creating session maker: {e}")


def init_db():
    """
    Initializes the database by creating all defined tables.
    """
    try:
        # engine = create_engine(DATABASE_URL)
        print("Initializing database...")
        engine = get_engine()
        print(f"Using engine: {engine}")
        print(f"Base metadata: {Base.metadata.tables}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error("Error initializing database: %s", e)
        print(f"Error initializing database: {e}")


# def get_engine():
#     """
#     Creates and returns a SQLAlchemy engine using the DATABASE_URL from the environment.
#     """
#     try:
#         return create_engine(DATABASE_URL)
#     except SQLAlchemyError as e:
#         logger.error("Error creating engine: %s", e)
#         raise


# def create_sessionmaker():
#     """
#     Creates and returns a sessionmaker factory bound to the engine.
#     """
#     engine = get_engine()
#     return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def init_db():
#     """
#     Initializes the database by creating all defined tables.
#     """
#     try:
#         engine = get_engine()
#         Base.metadata.create_all(bind=engine)
#         logger.info("Database initialized successfully")
#     except SQLAlchemyError as e:
#         logger.error("Error initializing database: %s", e)
#         raise


@asynccontextmanager
async def get_sqlalchemy_session():
    """
    Provides a SQLAlchemy session for asynchronous context management.
    """
    # session_maker = create_sessionmaker()
    # session = session_maker()
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
    # session_maker = create_sessionmaker()
    # session = session_maker()
    # return session
    return Session()
