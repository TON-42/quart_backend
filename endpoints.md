# API Endpoints

## `/get-user` [POST] (userId)
```
Get all information about a user (including chats)
```
## `/add-user-to-agreed` [POST] (chatId, userId)
```
Adds a user to the agreed users of the chat
```
## `/sell-chat` [POST] (chatId)
```
Changes the status of the chat to sold
```
## `/send-code` [POST] (phone_number)
```
Send a code to a user's phone
```

## `/send-message` [POST] (phone_number, chats)
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

## `/delete-user?id=123` [GET]
```
Delete 1 user
```

## `/delete-chat?id=123` [GET]
```
Delete 1 chat
```

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
