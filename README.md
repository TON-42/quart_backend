# Quart Backend

This repository contains a Quart backend application integrated with SQLAlchemy and Alembic for database management.

## Prerequisites

- Python 3.7+
- PostgreSQL database
- Telegram API credentials

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/TON-42/quart_backend.git
   cd quart_backend
   ```

2. Create and activate a virtual environment:

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Create a `.env` file in the root directory and add the following:

   ```env
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

5. Initialize the database:

   ```sh
   alembic upgrade head
   ```

## Running the Application

1. Start the Quart server:

   ```sh
   python3 cashAndPayBot.py
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

## Database Migrations

1. Create a new migration script:

   ```sh
   alembic revision --autogenerate -m "Migration message"
   ```

2. Apply the migration:

   ```sh
   alembic upgrade head
   ```
