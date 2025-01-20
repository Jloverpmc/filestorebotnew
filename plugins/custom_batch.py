from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id
import base64

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('custom_batch'))
async def custom_batch(client: Client, message: Message):
    messages = []
    is_cancel = False
    hi = await message.reply_text("Send the message you want to store:")
    first = await client.listen(message.from_user.id)
    messages.append(first.text.strip())
    await hi.delete()
    await first.delete()
    while True:
        text = f"Stored Messages: {len(messages)}\n\nPlease click your preferred button:"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Message", callback_data="add_message")],
            [InlineKeyboardButton("Generate Sharable Link", callback_data="generate_link")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ])
        sent_message = await message.reply_text(text, reply_markup=buttons)
        response = await client.wait_for_click(message.chat.id)

        if response.data == "add_message":
            await response.message.delete()
            prompt = await message.reply_text("Send the next message you want to store:")
            new_message = await client.listen(message.from_user.id)
            messages.append(new_message.text.strip())
            await prompt.delete()
            await new_message.delete()
            await sent_message.delete()
        elif response.data == "generate_link":
            await sent_message.delete()
            break
        elif response.data == "cancel":
            await sent_message.delete()
            await message.reply_text("Operation canceled. Goodbye!")
            is_cancel = True
            break
    if is_cancel:
        return
    encoded_data = "custombatch-" + base64.urlsafe_b64encode("|".join(messages).encode()).decode()
    if len(encoded_data) > 65536:
        await message.reply_text("❌ Too many messages! Please reduce the number.")
        return
    link = f"https://t.me/{client.username}?start={encoded_data}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Share Link", url=f"https://telegram.me/share/url?url={link}")]
    ])
    await message.reply_text(f"Here is your sharable link:\n\n{link}", reply_markup=reply_markup)
