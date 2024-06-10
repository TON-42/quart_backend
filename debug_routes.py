from quart import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from models import User, Chat, ChatStatus
from db import Session

debug_routes = Blueprint('debug_routes', __name__)


# ------------------ DEBUG routes ---------------------------
@debug_routes.route("/get-users", methods=["GET"])
async def get_users():
    try:
        # Create a session
        session = Session()
        
        # Query all users
        users = session.query(User).options(joinedload(User.chats)).all()

        # Close the session
        session.close()
        
        users_json = [
            {
                "id": user.id,
                "name": user.name,
                "has_profile": user.has_profile,
                "words": user.words,
                "chats": [chat.id for chat in user.chats]
            }
            for user in users
        ]
        
        return jsonify(users_json)
    
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500


@debug_routes.route("/get-chats", methods=["GET"])
async def get_chats():
    try:
        # Create a session
        session = Session()
        
        # Query all chats
        chats = session.query(Chat).options(
            joinedload(Chat.agreed_users),
            joinedload(Chat.users)
        ).all()

        # Close the session
        session.close()
        
        chats_json = [
            {
                "id": chat.id,
                "name": chat.name,
                "words": chat.words,
                "status": chat.status.name,  # Convert enum to string
                "lead": chat.lead_id,
                "full_text": chat.full_text,
                "agreed_users": [user.id for user in chat.agreed_users],
                "users": [user.id for user in chat.users]
            }
            for chat in chats
        ]
        
        return jsonify(chats_json)
    
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500


@debug_routes.route("/delete-user", methods=["GET"])
async def delete_user():
    try:
        # Create a session
        session = Session()
        
        try:
            # Query the user by ID
            user = session.query(User).filter(User.id == 122493869).one()
            
            # Delete the user
            session.delete(user)
            session.commit()
            
            response = {"message": f"User has been deleted."}
            status_code = 200

        except NoResultFound:
            response = {"error": f"No user found."}
            status_code = 404

        except IntegrityError as e:
            session.rollback()
            response = {"error": f"Integrity error occurred: {str(e)}"}
            status_code = 500

    except Exception as e:
        session.rollback()
        response = {"error": f"An error occurred: {str(e)}"}
        status_code = 500

    finally:
        session.close()
        
    return jsonify(response), status_code

@debug_routes.route("/delete-chat", methods=["GET"])
async def delete_chat():
    try:
        # Create a session
        session = Session()
        
        try:
            # Query the user by ID
            chat = session.query(Chat).filter(Chat.id == 1942086946).one()
            
            # Delete the chat
            session.delete(chat)
            session.commit()
            
            response = {"message": f"Chat has been deleted."}
            status_code = 200

        except NoResultFound:
            response = {"error": f"No chat found."}
            status_code = 404

        except IntegrityError as e:
            session.rollback()
            response = {"error": f"Integrity error occurred: {str(e)}"}
            status_code = 500

    except Exception as e:
        session.rollback()
        response = {"error": f"An error occurred: {str(e)}"}
        status_code = 500

    finally:
        session.close()
        
    return jsonify(response), status_code

@debug_routes.route("/create-user", methods=["GET"])
async def create_test_user():
    session = Session()
    status = 0
    response = jsonify({"message": "OK"}), 200
    # Query the database to check if a user with the provided ID exists
    try:
        print("ok")
        existing_user = session.query(User).filter(User.id == 3243252343).one()
        print("User already exists")
    except NoResultFound:
        new_user = User(id=3243252343, name="dantollllll", has_profile=False, words=0)
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "has_profile": new_user.has_profile,
            "words": new_user.words
        }

        print(user_data)
        session.add(new_user)
        session.commit()
        response =  jsonify(user_data), 200
        print("added")
    except Exception as e:
        print(f"Error: {str(e)}")
        response = jsonify({f"Error: {str(e)}"}), 400
    finally:
        session.close()
    return response

@debug_routes.route("/create-chat", methods=["GET"])
async def create_chat():
    # Enum for chat status
    status = 0
    try:
        session = Session()

        new_chat = Chat(id=32432525, name="Ton_stuff", words=12345, status=ChatStatus.pending, lead_id=32432524, full_text="123")

        lead = session.query(User).filter(User.id == 32432524).one()
        new_chat.lead = lead
        
        agreed_user_ids = [32432524]
        agreed_users = session.query(User).filter(User.id.in_(agreed_user_ids)).all()
        new_chat.agreed_users.extend(agreed_users)

        all_users = session.query(User).filter(User.id.in_([32432524, 32432525])).all()
        new_chat.users.extend(all_users)
    
        session.add(new_chat)
        session.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({f"Error: {str(e)}"}), 400
        status = 1
    finally:
        session.close()
        return jsonify({"message": "OK"}), 200
        # return status


# -----------------------------------------------