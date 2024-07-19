import logging
from quart import Quart, jsonify, request
from quart_cors import cors
from routes.debug_routes import debug_routes
from routes.login_route import login_route
from routes.user_route import user_route
from routes.chat_route import chat_route
from bot import bot
from telebot import types
from services.session_expiration import check_session_expiration
from db import init_db


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
    )


setup_logging()
logger = logging.getLogger(__name__)

init_db()

app = Quart(__name__)
app = cors(app, allow_origin="*")

app.register_blueprint(debug_routes)
app.register_blueprint(login_route)
app.register_blueprint(user_route)
app.register_blueprint(chat_route)


@app.before_serving
async def startup():
    app.add_background_task(check_session_expiration)
    logger.info("App started")


@app.after_serving
async def shutdown():
    for task in app.background_tasks:
        task.cancel()
    logger.info("App stopped")


@app.route("/health", methods=["GET"])
async def health():
    app.logger.info("Health check endpoint called")
    logger.info("Health check endpoint called")
    return "ok", 200


@app.route("/hello", methods=["GET"])
async def hello_world():
    logger.info("Hello world endpoint called")
    return jsonify({"message": "Hello, World!"})


@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        logger.info("Webhook received")
        data = await request.get_json()
        update = types.Update.de_json(data)
        await bot.process_new_updates([update])
    return "ok"


if __name__ == "__main__":
    app.run(port=8080)
