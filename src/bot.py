import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import Config

commands = "📝 /start - Start the bot\n❓ /faq - more information"

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

# @bot.message_handler(commands=["faq"])
# async def faq(message):
#     caption = """
#     ## General

#     **What is ChatPay?**
#     ChatPay is a platform that allows users to monetize their Telegram chats by bundling them into AI training datasets. Users can earn tokens by choosing which chats to submit and receiving payouts once their data is used.

#     **How does ChatPay work?**
#     Users select the Telegram chats they want to monetize. If all chat group members consent, the chats are anonymized, tagged, and bundled into datasets. These datasets are then sold to AI and chatbot model vendors, and users receive a share of the revenue.

#     ## Data and Privacy

#     **What type of data does ChatPay collect?**
#     Initially, ChatPay collects text data from Telegram chats. In the future, it will also include audio, video, and photos.

#     **How is my data protected?**
#     All data is anonymized by stripping it of any identifiers before it is tagged and bundled into datasets. This ensures that your personal information remains private.

#     **Do all chat members need to give consent?**
#     Yes, chats are only monetized if all group members give their full consent.

#     ## Earnings and Payouts

#     **How do I earn money with ChatPay?**
#     You earn money by submitting eligible chats for monetization. Once the datasets are sold, you receive a share of the revenue. You can view your estimated payout per chat directly in the Telegram mini-app.

#     **How will I receive my payouts?**
#     Payouts will be made using a utility token, $WORD, which will be available soon. Users can receive higher payouts by staking $WORD tokens, undergoing user verification, or becoming active community members.

#     ## Tokens and Staking

#     **What is the $WORD token?**
#     The $WORD token is a utility token that will be used for payouts to users. It will also be part of the token allocation for the team, early supporters, and testers.

#     **How can I earn higher payouts?**
#     You can earn higher payouts by staking $WORD tokens, undergoing user verification, or becoming an active member of the ChatPay community.

#     ## Getting Started

#     **How do I start using ChatPay?**
#     To get started, download the Telegram mini-app, choose the chats you want to monetize, and follow the prompts to submit your data. Make sure all chat members give their consent for monetization.

#     **Is there a roadmap for ChatPay?**
#     Yes, our roadmap includes the launch of the $WORD token, token allocation for the team and early supporters, and the addition of new data types such as audio, video, and photos.

#     ## Support and Community

#     **How can I get support if I have issues or questions?**
#     For support, you can contact our team directly through the Telegram mini-app or visit our website for more information.

#     **How can I become an active member of the ChatPay community?**
#     You can join our community by participating in discussions, providing feedback, and staying active in our Telegram groups and other social media channels.

#     **Where can I find more information about ChatPay?**
#     More information can be found on our website, within the Telegram mini-app, or by contacting our support team.
#     """

#     await bot.send_message(message.chat.id, caption, parse_mode='MarkdownV2')
