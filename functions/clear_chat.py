from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from database.class_Database import Database

db = Database()

from icecream import ic

async def clear_chat_window(message: Message, bot: Bot):
    try:
        for item in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, item)
    except TelegramBadRequest:
        pass

