from db import Session
from models import User, Chat, ChatStatus
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload


async def create_chat(
    chat_id, chat_name, words_number, sender_id, chat_users, teleg_id
):
    session = Session()
    status = 0
    try:
        # Query the database to check if a chat with the provided ID exists
        existing_chat = session.query(Chat).filter(Chat.id == chat_id).one()
        print(f"Chat {chat_name} already exists")
    except NoResultFound:
        print(f"Creating {chat_name} chat")
        new_chat = Chat(
            id=chat_id,
            name=chat_name,
            words=words_number,
            status=ChatStatus.pending,
            lead_id=sender_id,
            telegram_id=teleg_id,
        )

        lead = session.query(User).filter(User.id == sender_id).one()
        new_chat.lead = lead

        agreed_user_ids = [sender_id]
        agreed_users = session.query(User).filter(User.id.in_(agreed_user_ids)).all()
        new_chat.agreed_users.extend(agreed_users)

        all_users = session.query(User).filter(User.id.in_(chat_users)).all()
        new_chat.users.extend(all_users)

        session.add(new_chat)
        session.commit()
    except Exception as e:
        print(f"Error in create_chat: {str(e)}")
        status = 1
    finally:
        session.close()
        return status


async def add_chat_to_users(users_id, chat_id):
    status = 0
    try:
        session = Session()

        print(f"Adding chat:{chat_id} to users:{users_id}")
        # get 1 chat
        chat = session.query(Chat).filter(Chat.id == chat_id).one()
        # get all related users
        users = session.query(User).filter(User.id.in_(users_id)).all()

        # add the chat to each user
        for user in users:
            if chat not in user.chats:
                user.chats.append(chat)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
        status = 1
    finally:
        session.close()
        return status
