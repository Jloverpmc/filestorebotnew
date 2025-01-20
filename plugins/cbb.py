from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, START_MSG
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery



@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>🤖 My Name :</b> {client.me.mention} \n<b>📝 Language :</b> <a href='https://python.org'>Python 3</a> \n<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram {__version__}</a> \n<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a> \n<b>📢 Channel :</b> <a href='https://t.me/Madflix_Bots'>MadflixBotz</a> \n<b>🧑‍💻 Developer :</b> <a href='tg://user?id={OWNER_ID}'>MaadflixOfficials</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏡 Home", callback_data = "home"),
                 InlineKeyboardButton("🔒 Close", callback_data = "close")]
            ])
        )    

    if data == "home":
        await query.message.edit_text(
            text = START_MSG.format(
                first = query.from_user.first_name,
                last = query.from_user.last_name,
                username = None if not query.from_user.username else '@' + query.from_user.username,
                mention = query.from_user.mention,
                id = query.from_user.id
            ),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("😊 About Me", callback_data = "about"),
                 InlineKeyboardButton("🔒 Close", callback_data = "close")]
            ])
        )  

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass





# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
