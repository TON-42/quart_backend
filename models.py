from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
if not dotenv_path:
    raise FileNotFoundError("No .env file found")

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
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)
