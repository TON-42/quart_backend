async def get_chat_id(dialog_id, sender_id, client):
    chat_users = []
    users = await client.get_participants(dialog_id)
    for user in users:
        chat_users.append(user.id)
    chat_users.append(sender_id)
    private_chat_id = '_'.join(str(num) for num in sorted(chat_users))
    return (private_chat_id)

async def count_words(dialog_id, client):
    word_count = 0
    async for message in client.iter_messages(dialog_id):
        if message.text:
            words = message.text.split()
            word_count += len(words)
            if word_count > 2000:
                break
    return word_count
