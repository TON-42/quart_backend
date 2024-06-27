from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    Table,
    Text,
    create_engine,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ENUM
from dotenv import load_dotenv
from datetime import datetime
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
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column("chat_id", String(255), ForeignKey("chats.id"), primary_key=True),
)

# Association table for many-to-many relationship between agreed users and chats
agreed_users = Table(
    "agreed_users",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column("chat_id", String(255), ForeignKey("chats.id"), primary_key=True),
)

# Association table for many-to-many relationship between agreed users and chats
agreed_users_chats = Table(
    "agreed_users_chats",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column("chat_id", String(255), ForeignKey("chats.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    has_profile = Column(Boolean, default=False)
    words = Column(BigInteger, default=0)
    chats = relationship("Chat", secondary=users_chats, back_populates="users")
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    auth_status = Column(String(20), default="default", nullable=True)
    agreed_chats = relationship(
        "Chat", secondary=agreed_users_chats, back_populates="agreed_users"
    )


class Chat(Base):
    __tablename__ = "chats"
    id = Column(String(255), primary_key=True)
    name = Column(String(100), nullable=False)
    words = Column(BigInteger, default=0)
    status = Column(ENUM(ChatStatus), nullable=False)
    lead_id = Column(BigInteger, ForeignKey("users.id"))
    lead_name = Column(String(100), nullable=False)
    lead = relationship("User", foreign_keys=[lead_id])
    agreed_users = relationship(
        "User", secondary=agreed_users_chats, back_populates="agreed_chats"
    )
    users = relationship("User", secondary=users_chats, back_populates="chats")


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
