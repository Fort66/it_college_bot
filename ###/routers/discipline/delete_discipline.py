from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards

from states.other_states import DisciplineState
from routers.discipline.select_discipline import discipline_selection


delete_discipline_router = Router()


@delete_discipline_router.callback_query(F.data.startswith("delete_discipline"))
async def create_discipline(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.answer()
    kb = Keyboards('keyboards/teachers/disciplines/delete_discipline')
    await bot.send_message(chat_id=call.from_user.id, text=load_file("messages/teachers/disciplines/delete_discipline"), reply_markup=await kb.inline_kb_generator(2))


@delete_discipline_router.callback_query(F.data.startswith("yes_delete_discipline"))
async def create_discipline(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    db = Database()
    await db.delete_discipline(discipline_selection.value)
    await call.answer(text=load_file("messages/teachers/disciplines/delete_success"))
    await call.answer()
    await clear_chat(bot=bot, message=call.message)

@delete_discipline_router.callback_query(F.data.startswith("no_delete"))
async def delete_discipline(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    kb = Keyboards("keyboards/teachers/general/main")
    await call.message(text=load_file("messages/teachers/disciplines/no_delete_discipline"), reply_markup=await kb.inline_kb_generator(2))
    await call.answer()


