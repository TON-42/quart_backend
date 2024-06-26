## API Endpoints

- `/get-user` [POST]

- `/send-code` [POST]

- `/login` [POST]

- `/send-message` [POST]

- `/add-user-to-agreed` [POST]

- `/is-active` [POST]

- `/health` [GET]

## DEBUG API Endpoints

- `/get-users` [GET]

- `/get-chats` [GET]

- `/delete-all-users` [GET]

- `/delete-all- chats` [GET]

- `/delete-user?id=123` [GET]

- `/delete-chat?id=123` [GET]

<br>
<br>


## Endpoints Detailed

<details>
<summary><h3>/get-user</h3></summary>

- **Method**: `POST`
- **Description**: Fetches user data based on the provided user ID and optional username.
- **Request Body**:

  - `userId` (number, required): The unique identifier of the user.
  - `username` (string, optional): The username of the user.

  ```json
  {
    "userId": 123,
    "username": "john_doe"
  }
  ```

- **Responses**:
  - **200 OK**: Returns user data including profile and chat information.
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "has_profile": true,
      "words": [],
      "chats": [
        {
          "id": 1,
          "name": "Chat with Team",
          "words": 120,
          "status": "active",
          "lead_id": 1,
          "agreed_users": [2, 3],
          "users": [1, 2, 3]
        }
      ]
    }
    ```
  - **400 Bad Request**: Returned if `userId` is missing from the request.
    ```json
    {
      "error": "userId is missing"
    }
    ```
  - **404 Not Found**: Returned if the user does not exist.
    ```json
    {
      "message": "User with id 123 does not exist"
    }
    ```
  - **500 Internal Server Error**: Returned if there is an internal error.
    ```json
    {
      "error": "Internal error"
    }
    ```
</details>

<details>
<summary><h3>/send-code</h3></summary>

- **Method**: `POST`
- **Description**: Sends an authotization code to a phone number of the user
- **Request Body**:

  - `phone_number` (string, required): The phone number of the user.

  ```json
  {
    "phone_number": "+37120455123",
  }
  ```

- **Responses**:
  - **200 OK**: Returns OK.
    ```json
    {
      "message": "ok"
    }
    ```
  - **400 Bad Request**: Returned if `phone_number` is missing from the request.
    ```json
    {
      "error": "phone_number is missing"
    }
    ```
  - **403 Forbidden**: Returned if `phone number` has been banned from Telegram
    ```json
    {
      "error": "phone_number has been banned"
    }
    ```
  - **404 Not Found**: Returned if phone number is invalid.
    ```json
    {
      "error": "PhoneNumberInvalidError"
    }
    ```
   - **409 Conflict**: Returned if user is already logged in.
    ```json
    {
      "message": "user is already logged in"
    }
    ```
    - **429 Too Many Requests**: Returned if asked for the code too many times.
    ```json
    {
      "error": "asked for the code too many times"
    }
    ```
  - **500 Internal Server Error**: Returned if there is an internal error.
    ```json
    {
      "error": "Internal error"
    }
    ```
</details>

<details>
<summary><h3>/login</h3></summary>

- **Method**: `POST`
- **Description**: Logs in to the user account 
- **Request Body**:

  - `phone_number` (string, required): The phone number of the user.
  - `code` (number, required): The autherizartion code.
  ```json
  {
    "phone_number": "+37120455123",
    "code": 75129
  }
  ```

- **Responses**:
  - **200 OK**: Returns chat information(chat_id, chat_name, words).
    ```json
    {
      "message": {"(122493869, 'stefano')": 1825}
    }
    ```
  - **400 Bad Request**: Returned if `phone_number` or `code` is missing from the request or the confirmation `code` has expired
  or `code` is invalid.
    ```json
    {
      "error": "phone_number is missing"
    }
    ```
  - **401 Not Authorized**: Returned if two-steps verification is enabled
    ```json
    {
      "error": "two-steps verification is enabled"
    }
    ```
  - **404 Not Found**: Returned if phone number is invalid.
    ```json
    {
      "error": "PhoneNumberInvalidError"
    }
    ```
  - **409 Conflict**: Returned if user is already logged in.
    ```json
    {
      "message": "user is already logged in"
    }
    ```
  - **500 Internal Server Error**: Returned if there is an internal error.
    ```json
    {
      "error": "Internal error"
    }
    ```
</details>

<details>
<summary><h3>/is-active</h3></summary>

- **Method**: `POST`
- **Description**: Checks if we are still logged in to the user account
- **Request Body**:

  - `userId` (number, required): The unique identifier of the user.
  ```json
  {
    "userId": 84375302,
  }
  ```

- **Responses**:
  - **200 OK**: Returns OK.
    ```json
    {
      "message": "ok"
    }
    ```
  - **400 Bad Request**: Returned if `userId` is missing from the request.
    ```json
    {
      "message": "userId is missing"
    }
    ```
  - **404 Not Found**: Returned if session is not found.
    ```json
    {
      "message": "Not Found"
    }
    ```
  - **500 Internal Server Error**: Returned if there is an internal error.
    ```json
    {
      "error": "Internal error"
    }
    ```
</details>

<details>
<summary><h3>/add-user-to-agreed</h3></summary>

- **Method**: `POST`
- **Description**: Adds a user to the agreed group of the chat and checks if all users have agreed
- **Request Body**:

  - `userId` (number, required): The unique identifier of the user.
  - `chatId` (number, required): The unique identifier of the chat.
  ```json
  {
    {"userId": 143545, "chatId": 153500},
    {"userId": 243434, "chatId": 767601},
  }
  ```

- **Responses**:
  - **200 OK**: Returns a list of chats with status(sold, pending, declined, error).
    ```json
    {
      "21214": "pending",
      "545646": "error"
    }
    ```
  - **400 Bad Request**: Returned if `userId` or `chatId` is missing from the request.
    ```json
    {
      "message": "userId is missing"
    }
    ```
  - **500 Internal Server Error**: Returned if there is an internal error.
    ```json
    {
      "error": "Internal error"
    }
    ```
</details>

<details>
<summary><h3>/send-message</h3></summary>

- **Method**: `POST`
- **Description**: Sends a message to specified chats and updates user profiles.
- **Request Body**:

  - `phone_number` (string, required): The phone number of the user sending the message.
  - `message` (string, optional): The message to be sent. If not provided, a default message will be used.
  - `chats` (object, required): A dictionary where keys are chat details in the format `"(chat_id, 'chat_name')"` and values are the number of words associated with the chat.
  
  Example:
  ```json
  {
    "phone_number": "1234567890",
    "message": "Hello! This is a custom message.",
    "chats": {
      "(12345, 'Chat A')": 1000,
      "(67890, 'Chat B')": 2000
    }
  }
  ```

- **Responses**:
  - **200 OK**: Returns a list of users to whom the message was sent.
    ```json
    {
      "userB": ["username1", "username2"]
    }
    ```
  - **400 Bad Request**: Returned if `phone_number` or `chats` is missing from the request.
    ```json
    {
      "message": "No phone_number provided"
    }
    ```
    ```json
    {
      "message": "No chats were send"
    }
    ```
  - **500 Internal Server Error**: Returned if there is an internal error or if user creation fails.
    ```json
    {
      "error": "Could not create a user"
    }
    ```

- **Details**:
  1. The endpoint extracts `phone_number`, `message`, and `chats` from the request body.
  2. If `phone_number` is missing, it returns a `400 Bad Request` response.
  3. If `message` is not provided, a default message is used.
  4. If `chats` is missing, it returns a `400 Bad Request` response.
  5. The endpoint fetches the client associated with `phone_number` and updates the user profile.
  6. For each chat in `chats`, it:
     - Parses the chat details.
     - Retrieves the participants of the chat.
     - Creates users for the participants and sends the specified message.
     - Adds the chat to the user's list of chats.
  7. If an error occurs during processing, it logs out the user and deletes the client.
  8. Finally, it returns the list of users to whom the message was sent.

</details>


<details>
<summary><h2>Legacy</h2></summary>

- `/create-user` [GET]

```
Create 1 user (hardcoded)
```

- `/create-chat` [GET]

```
Create 1 chat (hardcoded)
```

## Authorization with JWT(JSON Web Tokens)

### 1. Connect to API

Make a call to `/access` with credentials in JSON

```
data = {"username": API_USERNAME, "password": API_PASSWORD}
```

### 2. Receive access token from `/access` response and store it

Store it to access other routes

### 3. Make a request to other routes with a token in a header

API should know that logged in user accessed it

```
headers = { "Authorization": f"Bearer {access_token}" }
```

</details>
