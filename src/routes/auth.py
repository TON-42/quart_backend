# src/routes/auth.py

from quart import Blueprint, jsonify, request
from quart_jwt_extended import JWTManager, create_access_token, jwt_required
from config import Config

auth = Blueprint("auth", __name__)


# JWT configuration
def configure_jwt(app):
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    JWTManager(app)


@auth.route("/access", methods=["POST"])
async def access():
    data = await request.get_json()
    username = data.get("username", None)
    password = data.get("password", None)

    if username != Config.API_USERNAME or password != Config.API_PASSWORD:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@auth.errorhandler(401)
async def custom_401(error):
    return jsonify({"msg": "Unauthorized access"}), 401
