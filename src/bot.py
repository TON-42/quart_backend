"""
Functions to handle the bot commands and messages.
"""

from telebot.async_telebot import AsyncTeleBot  # type: ignore
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo  # type: ignore
from config import Config

COMMANDS = "📝 /start - Start the bot\n" "❓ /faq - More information"

bot = AsyncTeleBot(Config.TOKEN)


async def global_message(users, message):
    """
    Send a message to all users in the database.
    """
    for user in users:
        if user.id < 100:
            continue
        print(f"sending to {user.name}")
        try:
            await bot.send_message(user.id, message)
        except Exception as e:
            print(f"error on {user.id}: {e}")
            continue


async def chat_sale(users):
    """
    Send a message when a chat is sold.
    """
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            "Discord", url="https://discord.com/channels/1249074503007600731/"
        )
    )
    markup.add(InlineKeyboardButton("X", url="https://x.com/chatpay_app"))
    for user in users:
        if user.id < 100:
            continue
        print(f"sending to {user.name}")
        try:
            await bot.send_message(
                user.id,
                "Congratulations! 🎉\nEvery user has agreed to sell the chat\nYour $WORD is on the way!\nJoin the community on Discord and X and let your friends know about ChatPay 💬 = 💰",
                reply_markup=markup,
            )
        except Exception as e:
            print(f"error on {user.id}: {e}")
            continue


@bot.message_handler(COMMANDS=["start"])
async def start(message):
    """
    Start command to send a welcome message to the user.
    """
    image_url = (
        "https://magnumtravel-bucket.s3.amazonaws.com/static/images/bot-banner.png"
    )
    caption = (
        "Welcome to ChatPay 💬\n\n"
        "1️⃣ Enter your phone number (don't forget your country code!). 📱\n\n"
        "2️⃣ Approve our terms & conditions. 📖\n\n"
        "3️⃣ Choose the chats you want to sell based on our estimated reward. ✅\n\n"
        "4️⃣ Send the consent approval to your chat partner. 📩\n\n"
        "5️⃣ Hold on tight while your $WORD arrives. 💸\n\n\n"
        "Empowering users one chat at the time! 💪"
    )

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    web_url = WebAppInfo("https://new-vite-frontend.vercel.app/")
    markup.add(InlineKeyboardButton("Let's go", web_app=web_url))
    markup.add(InlineKeyboardButton("Follow us", url="https://x.com/chatpay_app"))

    print(f"chat-id: {message.chat.id}")
    await bot.send_photo(message.chat.id, image_url, caption, reply_markup=markup)


@bot.message_handler(content_types=["text"])
async def message_reply(message):
    """
    Reply to the user with a list of available commands.
    """
    await bot.send_message(message.chat.id, f"List of available commands:\n{COMMANDS}")
