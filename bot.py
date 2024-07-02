import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import Config

commands = "📝 /start - Start the bot\n"

bot = AsyncTeleBot(Config.TOKEN)

async def global_message(users, message):
    for user in users:
        if user.id < 100:
            continue
        print(f"sending to {user.name}")
        try:
            await bot.send_message(user.id, message)
        except Exception:
            print(f"error on {user.id}")
            continue

async def chat_sale(users):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Discord", url="https://discord.com/channels/1249074503007600731/"))
    markup.add(InlineKeyboardButton("X", url="https://x.com/chatpay_app"))
    for user in users:
        if user.id < 100:
            continue
        print(f"sending to {user.name}")
        try:
            await bot.send_message(user.id, f"Congratulations! 🎉\nEvery user has agreed to sell the chat\nYour $WORD is on the way!\nJoin the community on Discord and X and let your friends know about ChatPay 💬 = 💰", reply_markup=markup)
        except Exception:
            print(f"error on {user.id}")
            continue
# Both you and XXX agreed to sell the chat
# Every user of the XXX chat agreed to sell the chat.
# We saved your points on our database, $WORD coming soon, join the community[DISCORD] 
@bot.message_handler(commands=["start"])
async def start(message):
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
    webUrl = WebAppInfo("https://new-vite-frontend.vercel.app/")
    markup.add(InlineKeyboardButton("Let's go", web_app=webUrl))
    markup.add(InlineKeyboardButton("Follow us", url="https://x.com/chatpay_app"))

    print(f"chat-id: {message.chat.id}")
    await bot.send_photo(message.chat.id, image_url, caption, reply_markup=markup)

@bot.message_handler(content_types=["text"])
async def message_reply(message):
    await bot.send_message(message.chat.id, "List of avaliable commands:\n" + commands)
