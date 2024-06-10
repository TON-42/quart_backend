from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# POSTGRES_USER = os.getenv("POSTGRES_USER")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
# POSTGRES_DB = os.getenv("POSTGRES_DB")
# POSTGRES_PORT = os.getenv("POSTGRES_PORT")
# POSTGRES_HOST = os.getenv("POSTGRES_HOST")
# DATABASE_URL = os.getenv("DATABASE_URL")

# async def get_db_pool():
#     return await asyncpg.create_pool(
#         user=POSTGRES_USER,
#         password=POSTGRES_PASSWORD,
#         database=POSTGRES_DB,
#         host=POSTGRES_HOST,
#         port=POSTGRES_PORT
#     )

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session maker bound to the engine
Session = sessionmaker(bind=engine)