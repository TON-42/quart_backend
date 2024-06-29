from shared import user_clients

async def get_chat_id(dialog_id, sender_id, phone_number):
    users = await user_clients[phone_number].get_client().get_participants(dialog_id)
    for user in users:
        chat_users.append(user.id)
    chat_users.append(sender_id)
    private_chat_id = '_'.join(str(num) for num in sorted(chat_users))
    return (private_chat_id)
    