
# Quart Backend

This repository contains a Quart backend application integrated with SQLAlchemy and Alembic for database management containerized with Docker for local development.

## Prerequisites

- Docker

## Creating image

Before creating an image don't forget to add your `.env` file to the root folder.

```
   docker build -t quart_app .
```

## Running the Application

```
   docker run -p 8080:8080 quart_app
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

## Manually log into docker container

```
docker exec -it {container_id} /bin/sh
```

## Database Management

Current version works with deployed Digital Ocean database. Will set up local db ASAP. 

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
