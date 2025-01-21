from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import base64
from pyrogram import Client, filters
from bot import Bot
from config import ADMINS
from helper_func import encode
import asyncio
from config import ADMINS, DB_URL
from pymongo import MongoClient
import random
import string
import asyncio

# Initialize MongoDB Client
mongo_client = MongoClient(DB_URL)
db = mongo_client["custom_batch_bot"]
collection = db["batches"]

# Shared dictionary to store session data for users
session_data = {}


def generate_random_id():
    """Generate a random 8-character alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def save_batch_to_db(random_id, messages):
    """Save batch messages to MongoDB."""
    collection.insert_one({"_id": random_id, "messages": messages})

def get_batch_from_db(random_id):
    """Retrieve batch messages from MongoDB using the random ID."""
    result = collection.find_one({"_id": random_id})
    return result["messages"] if result else None


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('custom_batch'))
async def custom_batch(client: Client, message: Message):
    user_id = message.from_user.id
    session_data[user_id] = {
        "messages": [],
        "is_cancel": False
    }

    hi = await message.reply_text("Send the message you want to store:")
    first = await client.listen(user_id)
    session_data[user_id]["messages"].append(first.text.strip())
    await hi.delete()
    await first.delete()

    sent_message = await message.reply_text(
        f"Stored Messages: {len(session_data[user_id]['messages'])}\n\nPlease click your preferred button:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Message", callback_data=f"add_message_{user_id}")],
            [InlineKeyboardButton("Generate Sharable Link", callback_data=f"generate_link_{user_id}")],
            [InlineKeyboardButton("Cancel", callback_data=f"cancel_{user_id}")]
        ])
    )
    session_data[user_id]["sent_message"] = sent_message


@Bot.on_callback_query(filters.regex(r"add_message_\d+"))
async def add_message_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in session_data:
        await callback_query.message.reply_text("❌ Session expired or invalid!")
        return

    await callback_query.message.delete()
    prompt = await callback_query.message.reply_text("Send the next message you want to store:")
    new_message = await client.listen(user_id)
    session_data[user_id]["messages"].append(new_message.text.strip())
    await prompt.delete()
    await new_message.delete()

    sent_message = await callback_query.message.reply_text(
        f"Stored Messages: {len(session_data[user_id]['messages'])}\n\nPlease click your preferred button:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Message", callback_data=f"add_message_{user_id}")],
            [InlineKeyboardButton("Generate Sharable Link", callback_data=f"generate_link_{user_id}")],
            [InlineKeyboardButton("Cancel", callback_data=f"cancel_{user_id}")]
        ])
    )

    session_data[user_id]["sent_message"] = sent_message


@Bot.on_callback_query(filters.regex(r"generate_link_\d+"))
async def generate_link_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in session_data:
        await callback_query.message.reply_text("❌ Session expired or invalid!")
        return

    await session_data[user_id]["sent_message"].delete()
    messages = session_data[user_id]["messages"]
    random_id = generate_random_id()
    save_batch_to_db(random_id, messages)
    link = f"https://t.me/{client.username}?start={random_id}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Share Link", url=f"https://telegram.me/share/url?url={link}")]
    ])
    await callback_query.message.reply_text(f"Here is your sharable link:\n\n{link}", reply_markup=reply_markup)
    del session_data[user_id]


@Bot.on_callback_query(filters.regex(r"cancel_\d+"))
async def cancel_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in session_data:
        await callback_query.message.reply_text("❌ Session expired or invalid!")
        return

    await session_data[user_id]["sent_message"].delete()
    await callback_query.message.reply_text("Operation canceled. Goodbye!")
    del session_data[user_id]
