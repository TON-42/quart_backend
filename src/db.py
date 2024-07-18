from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import logging

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")


# Create engine and session in a function to avoid import-time side effects
def get_engine():
    return create_engine(DATABASE_URL)


def create_sessionmaker():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


# # Create SQLAlchemy engine
# engine = create_engine(DATABASE_URL)

# # Create session maker bound to the engine
# Session = sessionmaker(bind=engine)


# Initialize the database (create tables)
def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
