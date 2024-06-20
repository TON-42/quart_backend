
# Quart Backend

This repository contains a Quart backend application integrated with SQLAlchemy and Alembic for database management containerized with Docker for local development.

## Prerequisites

- Docker

## Build and run containers

Before runnung container don't forget to add your `.env` file to the root folder.

Your `.env` should have the following fields
```
BOT_TOKEN=bot_token
API_ID=my_id
API_HASH=my_hash

POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=my_db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://{username}:{password}@db:5432/{my_db}

```

Now you can build and run containers:
```
   docker-compose up --build
```

Since there is a volume:
```    
   volumes:
   - .:/app
```

You can make changes to local files, and they will immediately reflect inside the container. There is no need to rebuild the container for updates.

## Manually log into docker container if needed

```
docker exec -it {container_id} /bin/sh
```

## Remove containers
```
   docker-compose down
```

## Remove images
```
   docker rmi {image}
```

## Remove volume
```
   docker volume rm {volume}
```

2. The server will be running at `http://localhost:8080`.

## API Endpoints

- `GET /health`: Health check endpoint.
- `GET /hello`: Returns a hello message.
- `POST /login`: Handles user login with Telegram.
- `POST /send-code`: Sends the login code to the user's phone number.
- `POST /send-message`: Sends a message in a specific chat.
- `POST /users`: Creates a new user in the database.
- `GET /users`: Retrieves all users from the database.


### SQLAlchemy

SQLAlchemy is the ORM (Object Relational Mapper) used in this project. It allows us to define our database models as Python classes and provides a high-level API to interact with the database.

#### Example

Here's a very basic example of a SQLAlchemy model:

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

### Alembic

Alembic is a database migration tool for SQLAlchemy. It helps manage database schema changes over time, ensuring that the database schema is always in sync with the application code.

#### Common Commands

1. Create a new migration script:

   ```sh
   alembic revision --autogenerate -m "Migration message"
   ```

2. Apply the migration:

   ```sh
   alembic upgrade head
   ```

3. View the current status of migrations:

   ```sh
   alembic current
   ```

4. Downgrade to a previous migration:

   ```sh
   alembic downgrade -1
   ```
