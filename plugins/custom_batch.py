from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import base64
from pyrogram import Client, filters
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('custom_batch'))
async def custom_batch(client: Client, message: Message):
    messages = []
    is_cancel = False
    hi = await message.reply_text("Send the message you want to store:")
    first = await client.listen(message.from_user.id)
    messages.append(first.text.strip())
    await hi.delete()
    await first.delete()
    sent_message = await message.reply_text(
        f"Stored Messages: {len(messages)}\n\nPlease click your preferred button:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Message", callback_data="add_message")],
            [InlineKeyboardButton("Generate Sharable Link", callback_data="generate_link")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ])
    )

    @Bot.on_callback_query(filters.regex("add_message"))
    async def add_message_handler(client: Client, callback_query: CallbackQuery):
        nonlocal sent_message
        await callback_query.message.delete()
        prompt = await callback_query.message.reply_text("Send the next message you want to store:")
        new_message = await client.listen(callback_query.from_user.id)
        messages.append(new_message.text.strip())
        await prompt.delete()
        await new_message.delete()
        sent_message = await callback_query.message.reply_text(
            f"Stored Messages: {len(messages)}\n\nPlease click your preferred button:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Add Message", callback_data="add_message")],
                [InlineKeyboardButton("Generate Sharable Link", callback_data="generate_link")],
                [InlineKeyboardButton("Cancel", callback_data="cancel")]
            ])
        )

    @Bot.on_callback_query(filters.regex("generate_link"))
    async def generate_link_handler(client: Client, callback_query: CallbackQuery):
        nonlocal sent_message, is_cancel
        await sent_message.delete()
        is_cancel = False
        encoded_data = "custombatch-" + base64.urlsafe_b64encode("|".join(messages).encode()).decode()
        if len(encoded_data) > 65536:
            await callback_query.message.reply_text("❌ Too many messages! Please reduce the number.")
            return
        link = f"https://t.me/{client.username}?start={encoded_data}"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Share Link", url=f"https://telegram.me/share/url?url={link}")]
        ])
        await callback_query.message.reply_text(f"Here is your sharable link:\n\n{link}", reply_markup=reply_markup)

    @Bot.on_callback_query(filters.regex("cancel"))
    async def cancel_handler(client: Client, callback_query: CallbackQuery):
        nonlocal sent_message, is_cancel
        is_cancel = True
        await sent_message.delete()
        await callback_query.message.reply_text("Operation canceled. Goodbye!")

    while not is_cancel:
        await asyncio.sleep(1)
