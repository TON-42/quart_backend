# API Endpoints

## `/get-user` [POST] (userId)

```
Get all information about a user (including chats)
```

## `/add-user-to-agreed` [POST] (chatId, userId)

```
Adds a user to the agreed users of the chat. If all users agreed, sends 202
```

## `/send-code` [POST] (phone_number)

```
Send a code to a user's phone
```

## `/send-message` [POST] (phone_number, chats, message)

```
Send a message to all chats that user chose
```

## `/login` [POST] (phone_number, code)

```
Login to a user account
```

## `/is-active` [POST] (userId)

```
Is a session still active?(are we still logged in as a user)
```

## `/health` [GET]

```
Check that an app is responding
```

# DEBUG API Endpoints

## `/get-users` [GET]

```
Get all users
```

## `/get-chats` [GET]

```
Get all chats
```

## `/delete-all-users` [GET]

```
Delete all users
```

## `/delete-all- chats` [GET]

```
Delete all chats
```

## `/delete-user?id=123` [GET]

```
Delete 1 user
```

## `/delete-chat?id=123` [GET]

```
Delete 1 chat
```

<br>
<br>
<br>
<br>

# Legacy

## `/create-user` [GET]

```
Create 1 user (hardcoded)
```

## `/create-chat` [GET]

```
Create 1 chat (hardcoded)
```

# Authorization with JWT(JSON Web Tokens)

## 1. Connect to API

Make a call to `/access` with credentials in JSON

```
data = {"username": API_USERNAME, "password": API_PASSWORD}
```

## 2. Receive access token from `/access` response and store it

Store it to access other routes

## 3. Make a request to other routes with a token in a header

API should know that logged in user accessed it

```
headers = { "Authorization": f"Bearer {access_token}" }
```

## Endpoints Detailed

### `/get-user`

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
