from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session maker bound to the engine
Session = sessionmaker(bind=engine)
