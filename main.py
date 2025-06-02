import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import (
    DialogManager,
    StartMode,
    setup_dialogs,
)
from dotenv import load_dotenv

from functions.clear_chat import clear_chat_window

load_dotenv()
from bot import bot
from database.class_Database import Database
from dialogs.class_DisciplineDialog import DisciplineDialog
from dialogs.class_QuestDialog import QuestDialog
from dialogs.class_StartDialog import StartDialog
from dialogs.class_TeacherDialog import TeacherDialog
from dialogs.class_AnswerDialog import AnswerDialog
from dialogs.class_GroupDialog import GroupsDialog
from dialogs.class_StudentListDialog import StudentListDialog
from source import main_menu_commands
from states import StartState

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


dialogues = [
    StartDialog().dialog,
    TeacherDialog().dialog,
    DisciplineDialog().dialog,
    QuestDialog().dialog,
    AnswerDialog().dialog,
    GroupsDialog().dialog,
    StudentListDialog().dialog,
]


setup_dialogs(dp)


@dp.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    await clear_chat_window(message, bot)
    await dialog_manager.start(StartState.start, mode=StartMode.RESET_STACK)


async def main():
    dp.include_routers(*dialogues)
    db = Database()
    await db.create_tables()
    await main_menu_commands(bot)
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
