from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    Table,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from db import Base
import enum


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
    telegram_id = Column(BigInteger, nullable=True, default=0)
    name = Column(String(100), nullable=False)
    words = Column(BigInteger, default=0)
    status = Column(ENUM(ChatStatus), nullable=False)
    lead_id = Column(BigInteger, ForeignKey("users.id"))
    lead = relationship("User", foreign_keys=[lead_id])
    agreed_users = relationship(
        "User", secondary=agreed_users_chats, back_populates="agreed_chats"
    )
    users = relationship("User", secondary=users_chats, back_populates="chats")
    full_text_data = relationship("ChatFullText", uselist=False, back_populates="chat")


class ChatFullText(Base):
    __tablename__ = "chat_full_texts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(String(255), ForeignKey("chats.id"))
    full_text = Column(Text, nullable=True)  # Field to store original chat text
    sanitized_text_presidio = Column(
        Text, nullable=True
    )  # Field to store sanitized chat text
    annotated_text_presidio = Column(
        Text, nullable=True
    )  # Field to store annotated chat text
    sanitized_text_chatgpt = Column(
        Text, nullable=True
    )  # Field to store sanitized chat text
    annotated_text_chatgpt = Column(
        Text, nullable=True
    )  # Field to store annotated chat text
    sanitized_text_local_llm = Column(
        Text, nullable=True
    )  # Field to store sanitized chat text
    annotated_text_local_llm = Column(
        Text, nullable=True
    )  # Field to store annotated chat text
    chat = relationship("Chat", back_populates="full_text_data")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Text, primary_key=True)
    phone_number = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True)
    phone_code_hash = Column(Text, nullable=True)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    send_code_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    is_logged = Column(Boolean, default=False, nullable=True)
    chats = Column(Text, nullable=True)
