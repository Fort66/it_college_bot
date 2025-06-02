from aiogram import Bot, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards
from states.teacher_states import StartBot

start_router = Router()

db = Database()

@start_router.message(CommandStart())
async def start(message: Message, bot: Bot):
    await clear_chat(message, bot)

    kb = Keyboards("keyboards/general/profile")

    await bot.send_message(
        message.from_user.id,
        load_file("messages/general/start"),
        reply_markup=await kb.inline_kb_generator(),
    )

# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram_dialog import Window
# from aiogram_dialog.widgets.kbd import Button
# from aiogram_dialog import DialogManager, StartMode
# from aiogram_dialog import Dialog
# from aiogram_dialog.widgets.text import Const, Format
# from aiogram_dialog import setup_dialogs

# from aiogram_dialog import Dialog, LaunchMode, Window
# from aiogram_dialog.about import about_aiogram_dialog_button
# from aiogram_dialog.widgets.kbd import Start, Group, Back, Next, Cancel, Row, Column


# from states.dialog_states import StartBot

# storage = MemoryStorage()

# start_dialog = Dialog(
#     Window(
#         Const(load_file("messages/general/start")),
#         Group(
#             Column(
#                 Button(Const("👨‍🏫 Преподаватель"), id="teachers"),
#                 Button(Const("🧑🏻‍🎓 Студент"), id="students"),
#                 ),
#             ),
#         state=StartBot.teachers,
#         ),
#     )


# @start_router.message(Command("start"))
# async def start(message: Message, dialog_manager: DialogManager, bot: Bot):
#     await clear_chat(message, bot)
#     # Важно: всегда устанавливайте `mode=StartMode.RESET_STACK`, чтобы не накапливать диалоги
#     await dialog_manager.start(StartBot.teachers, mode=StartMode.RESET_STACK)
