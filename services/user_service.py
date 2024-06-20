from db import Session
from models import User
from sqlalchemy.orm.exc import NoResultFound




async def create_user(user_id, username, profile):
    session = Session()
    try:
        # Query the database to check if a user with the provided ID exists
        existing_user = session.query(User).filter(User.id == user_id).one()
        # print("User already exists")
    except NoResultFound:
        new_user = User(
            id=user_id, name=username, has_profile=profile, words=0
        )
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "has_profile": new_user.has_profile,
            "words": new_user.words,
        }

        print(user_data)
        session.add(new_user)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        session.close()

async def update_profile(user_id, has_profile):
    session = Session()
    status = 0
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.has_profile = has_profile
        session.commit()
    except NoResultFound:
        print(f"User with ID {user_id} not found")
        status = 1
    except Exception as e:
        print(f"Error updating username or profile: {str(e)}")
        status = 1
    finally:
        session.close()
        return status