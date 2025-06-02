from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards

from states.other_states import DisciplineState
from routers.group.select_group import group_selection


delete_group_router = Router()


@delete_group_router.callback_query(F.data.startswith("delete_group"))
async def create_group(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.answer()
    kb = Keyboards('keyboards/teachers/groups/delete_group')
    await bot.send_message(chat_id=call.from_user.id, text=load_file("messages/teachers/groups/delete_group"), reply_markup=await kb.inline_kb_generator(2))


@delete_group_router.callback_query(F.data.startswith("yes_delete_group"))
async def create_group(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    db = Database()
    await db.delete_group(group_selection.value)
    await call.answer(text=load_file("messages/teachers/groups/delete_success"))
    await call.answer()
    await clear_chat(bot=bot, message=call.message)

@delete_group_router.callback_query(F.data.startswith("no_delete_group"))
async def delete_group(call: CallbackQuery, state: FSMContext, bot: Bot):
    # await call.message.delete()
    await clear_chat(call.message.message_id, bot)
    kb = Keyboards("keyboards/teachers/general/main")
    await call.message.answer(text=load_file("messages/teachers/groups/no_delete"), reply_markup=await kb.inline_kb_generator(2))
    await call.answer()


