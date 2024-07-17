import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

bot = AsyncTeleBot("5459758083:AAGEANF9VE42ygmyLB7MmAXqK40kQYb5wdM")


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    text = "Hi, I am EchoBot.\nJust write me something and I will repeat it!"
    await bot.reply_to(message, text)


@bot.message_handler(func=lambda message: True)
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
    markup.row_width = 1
    webUrl = WebAppInfo("https://new-vite-frontend.vercel.app/")
    markup.add(InlineKeyboardButton("Launch", web_app=webUrl))

    await bot.send_photo(message.chat.id, image_url, caption, reply_markup=markup)


# # Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# async def echo_message(message):
#     await bot.reply_to(message, message.text)


asyncio.run(bot.polling())
