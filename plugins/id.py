from pyrogram import Client, filters, enums
from pyrogram.types import Message




@Client.on_message(filters.command("id") & filters.private)
async def showid(client, message):
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f"<b>Your User ID Is :</b> <code>{message.from_user.id}</code>", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f"<b>This Group ID Is :</b> <code>{message.chat.id}</code>", quote=True)

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f"<b>This Channel ID Is :</b> <code>{message.chat.id}</code>", quote=True)






# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
