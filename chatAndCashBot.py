from quart import Quart, jsonify, request
from quart_cors import cors
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update, Bot
from telegram.ext import Dispatcher, CommandHandler, ChatMemberHandler, PollHandler, ContextTypes
from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import logging
from telethon.errors import SessionPasswordNeededError
from collections import defaultdict


# Load environment variables from .env file if present
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Quart(__name__)
app = cors(app, allow_origin="*")

client = TelegramClient("user", API_ID, API_HASH)

polls = {}

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN environment variable not set")
    exit(1)
bot: Bot = Bot(token=TOKEN)


async def start(update: Update, context):
    print("start command received")
    update.message.reply_text("ajsjdsafhjdf!")

def vote(update: Update, context):
    chat_member = update.my_chat_member

    # Check if the bot was added to the group
    if chat_member.new_chat_member.status == 'member':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="just arrived, whatsup"
        )
        message = context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question="Do you argee to sell your part of this chat",
            options=["I argee", "I do not argee"]
        )
        polls[message.poll.id] = (update.effective_chat.id, message.message_id)
        
def poll_monitor(update: Update, context: ContextTypes):
    poll = update.poll
    options = poll.options
    
    chat_id, message_id = polls.get(poll.id, (None, None))
    if chat_id is not None:
        if options[0].voter_count == 1 and options[1].voter_count == 0:
            context.bot.stop_poll(chat_id, message_id)
            context.bot.send_message(
                chat_id=chat_id,
                text="Every member in the group argeed to sell their chat history in this group"
            )
        if options[1].voter_count > 0:
            context.bot.stop_poll(chat_id, message_id)
            context.bot.send_message(
                chat_id=chat_id,
                text="Atleast one member declined, please consider later!"
            )


@app.route("/health", methods=["GET"])
async def health():
    app.logger.info("Health check endpoint called")
    return "ok", 200

@app.route('/hello', methods=['GET'])
async def hello_world():
    print("hello endpoint!!")
    return jsonify({"message": "Hello, World!"})

@app.route('/login', methods=['POST'])
async def login():
    print("login??????")
    data = await request.get_json()
    auth_code = data.get('code')
    print("auth code:")
    print(auth_code)
    phone_number = data.get('phone_number')
    print(phone_number)

    try:
        await client.sign_in(phone_number, auth_code)
    except SessionPasswordNeededError:
        return "401"
    
    count = 0
    res = defaultdict(int) # initializes res as a defaultdict that defaults to 0 for any new key

    if await client.is_user_authorized():
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            count += 1
            if (count > 10):
                break
            print(dialog.title)
            if dialog.id == 777000:
                continue
            async for message in client.iter_messages(dialog.id):
                if message.text is not None:
                    words = message.text.split()
                    res[dialog.name] += len(words)
                    if (res[dialog.name] > 2000):
                        break 
            # print(f"Chat '{dialog.name}' has words")
    first_key = list(res.keys())[0]
    await client.send_message(first_key, "test message, do not worry")
    await client.disconnect()
    return jsonify(res), 200

@app.route('/send-code', methods=['POST'])
async def send_code():
    print("send-code!!!!!!!!!!!!!")
    data = await request.get_json()
    phone_number = data.get('phone_number')
    print(phone_number)
    await client.connect()
    await client.send_code_request(phone_number)
    return "ok", 200


dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(ChatMemberHandler(vote, ChatMemberHandler.MY_CHAT_MEMBER))
dispatcher.add_handler(PollHandler(poll_monitor))

@app.route("/webhook", methods=["POST"])
async def webhook():
    print("entered webhook")
    app.logger.info("Webhook received")
    if request.method == "POST":
        data = await request.get_json()
        update = Update.de_json(data, bot)
        update.message.reply_text("webhook")
        dispatcher.process_update(update)
        # update = Update.de_json(request.get_json(force=True), bot)
        # update.message.reply_text("webhook")
        # dispatcher.process_update(update)
    return "ok"

if __name__ == "__main__":
    app.run(port=8080)

    # Process or return retrieved dialogs (e.g., list of chat titles)
    # except (PhoneNumberInvalidError, AuthCodeInvalidError) as e:
    #     return {"error": str(e)}, "400"  # Return specific error message
    

    # client = TelegramClient(f'session_{phone_number}', api_id, api_hash)
    # session_dict[phone_number] = client
    # try:
    #     await client.connect()
    # except OSError:
    #     print('Failed to connect')
