from quart import Blueprint, jsonify, request, g

# We don't have this functions we have in Node.js and GoLang: we need to write the validate function by ouself
# from init_data import validate, parse, InitDataParsed


class InitDataParsed:
    # Define the InitDataParsed class based on the TS interface
    def __init__(self, auth_date, hash, **kwargs):
        self.auth_date = auth_date
        self.hash = hash
        self.can_send_after = kwargs.get("can_send_after")
        self.chat = kwargs.get("chat")
        self.chat_type = kwargs.get("chat_type")
        self.chat_instance = kwargs.get("chat_instance")
        self.query_id = kwargs.get("query_id")
        self.receiver = kwargs.get("receiver")
        self.start_param = kwargs.get("start_param")
        self.user = kwargs.get("user")


authorize_route = Blueprint("authorize_route", __name__)

# Your secret bot token.
TOKEN = "1234567890:ABC"


@authorize_route.route("/authorize", methods=["POST"])
async def authorize():
    try:
        if not request.is_json:
            return jsonify({"error": "Request data must be JSON"}), 400
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 400

        auth_type, auth_data = auth_header.split(" ")
        if auth_type != "tma":
            return jsonify({"error": "Invalid auth type"}), 401

        try:
            validate(auth_data, TOKEN, {"expiresIn": 3600})
            init_data = parse(auth_data)
            g.init_data = (
                init_data  # Store init_data in the global context for this request
            )
            return jsonify({"message": "Authorized"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
