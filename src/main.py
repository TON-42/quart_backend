from quart import Quart, jsonify, request
from quart_cors import cors
from routes.debug_routes import debug_routes
from routes.login_route import login_route
from routes.user_route import user_route
from routes.chat_route import chat_route
from bot import bot
from telebot import types
from services.session_expiration import check_session_expiration


app = Quart(__name__)
app = cors(app, allow_origin="*")

app.register_blueprint(debug_routes)
app.register_blueprint(login_route)
app.register_blueprint(user_route)
app.register_blueprint(chat_route)


@app.before_serving
async def startup():
    app.add_background_task(check_session_expiration)


@app.after_serving
async def shutdown():
    for task in app.background_tasks:
        task.cancel()


@app.route("/health", methods=["GET"])
async def health():
    app.logger.info("Health check endpoint called")
    return "ok", 200


@app.route("/hello", methods=["GET"])
async def hello_world():
    return jsonify({"message": "Hello, World!"})


@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        data = await request.get_json()
        update = types.Update.de_json(data)
        await bot.process_new_updates([update])
    return "ok"


if __name__ == "__main__":
    app.run(port=8080)

# from quart_jwt_extended import JWTManager, create_access_token, jwt_required
# app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

# jwt = JWTManager(app)

# @app.route('/access', methods=['POST'])
# async def access():
#     data = await request.get_json()
#     username = data.get('username', None)
#     password = data.get('password', None)

#     # Replace with your user authentication logic
#     if username != API_USERNAME or password != API_PASSWORD:
#         return jsonify({"msg": "Bad username or password"}), 401

#     access_token = create_access_token(identity=username)
#     return jsonify(access_token=access_token), 200

# @app.errorhandler(401)
# async def custom_401(error):
#     return jsonify({"msg": "Unauthorized access"}), 401


# @app.route("/initialize-client", methods=["GET"])
# async def initialize_client():
#     phone_number = request.args.get("phone_number", "")

#     if phone_number not in user_clients:
#         user_clients[phone_number] = ClientWrapper(phone_number, API_ID, API_HASH)

#     client_info = {
#         "phone_number": phone_number,
#         "created_at": user_clients[phone_number].get_creation_time().isoformat()
#     }
#     print(len(user_clients))
#     return jsonify(client_info)
