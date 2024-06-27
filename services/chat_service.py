from db import Session
from models import User, Chat, ChatStatus
from sqlalchemy.orm.exc import NoResultFound

async def create_chat(chat_id, chat_name, words_number, sender_id, sender_name, chat_users, priv_id, is_priv):
    session = Session()
    status = 0
    try:
        # Query the database to check if a chat with the provided ID exists
        existing_chat = session.query(Chat).filter(Chat.id == chat_id).one()
        print("Chat already exists")
    except NoResultFound:
        new_chat = Chat(
            id=chat_id,
            name=chat_name,
            words=words_number,
            status=ChatStatus.pending,
            lead_id=sender_id,
            lead_name=sender_name,
            is_private=is_priv,
            private_id=priv_id,
            full_text="None",
        )

        lead = session.query(User).filter(User.id == sender_id).one()
        new_chat.lead = lead

        agreed_user_ids = [sender_id]
        agreed_users = session.query(User).filter(User.id.in_(agreed_user_ids)).all()
        new_chat.agreed_users.extend(agreed_users)

        all_users = (
            session.query(User).filter(User.id.in_(chat_users)).all()
        )
        new_chat.users.extend(all_users)

        session.add(new_chat)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        status = 1
    finally:
        session.close()
        return status
    
async def add_chat_to_users(users_id, chat_id):
    status = 0
    try:
        session = Session()

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