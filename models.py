from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)


# Database URL from environment variable or fallback
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")  # Debugging line
if DATABASE_URL is None:
    raise ValueError("No DATABASE_URL found in environment variables")

# Create engine
# engine = create_engine(DATABASE_URL)


# Create engine and session in a function to avoid import-time side effects
def get_engine():
    return create_engine(DATABASE_URL)


def get_session():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create session
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize database
def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


# # Initialize database
# def init_db():
#     Base.metadata.create_all(bind=engine)
