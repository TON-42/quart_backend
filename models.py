from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ENUM
from dotenv import load_dotenv
import os
import enum


load_dotenv()

Base = declarative_base()


# Enum for chat status
class ChatStatus(enum.Enum):
    pending = "pending"
    sold = "sold"
    declined = "declined"


# Association table for many-to-many relationship between users and chats
users_chats = Table(
    "users_chats",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
)

# Association table for many-to-many relationship between agreed users and chats
agreed_users = Table(
    "agreed_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    has_profile = Column(Boolean, default=False)
    words = Column(Integer, default=0)
    chats = relationship("Chat", secondary=users_chats, back_populates="users")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    words = Column(Integer, default=0)
    full_text = Column(Text, nullable=False)
    status = Column(ENUM(ChatStatus), nullable=False)
    lead_id = Column(Integer, ForeignKey("users.id"))
    lead = relationship("User", foreign_keys=[lead_id])
    agreed_users = relationship("User", secondary=agreed_users, back_populates="chats")
    users = relationship("User", secondary=users_chats, back_populates="chats_users")


# Database URL from environment variable or fallback
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")  # Debugging line
if DATABASE_URL is None:
    raise ValueError("No DATABASE_URL found in environment variables")


# Create engine and session in a function to avoid import-time side effects
def get_engine():
    return create_engine(DATABASE_URL)


def get_session():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize database
def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
