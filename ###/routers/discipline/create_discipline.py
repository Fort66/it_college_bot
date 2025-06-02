from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards

from states.other_states import DisciplineState
from routers.discipline.select_discipline import discipline_selection


create_discipline_router = Router()


@create_discipline_router.callback_query(or_f(F.data.startswith("create_discipline"),F.data.startswith("edit_discipline")))
async def create_discipline(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=load_file("messages/teachers/disciplines/add_discipline_name"),
        reply_markup=None,
    )

    await state.set_state(DisciplineState.name)

    await call.answer()

@create_discipline_router.message(DisciplineState.name)
async def create_discipline_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=message.text)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        text=load_file("messages/teachers/disciplines/add_discipline_shortname"),
        reply_markup=None,
    )

    await state.set_state(DisciplineState.short_name)


@create_discipline_router.message(DisciplineState.short_name)
async def create_discipline_short_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(short_name=message.text)

    discipline = await state.get_data()

    db = Database()

    if discipline_selection.value is None:
        await db.add_discipline(
            name=discipline["name"],
            short_name=discipline["short_name"],
            teacher_id=message.from_user.id,
        )
    else:
        await db.update_discipline(
            discipline_id=discipline_selection.value,
            name=discipline["name"],
            short_name=discipline["short_name"],
        )

    kb = Keyboards("keyboards/teachers/general/main")

    # await clear_chat(message, bot)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        text=load_file("messages/teachers/disciplines/discipline_success"),
        reply_markup=await kb.inline_kb_generator(2),
    )
    # await clear_chat(message, bot)
    await state.clear()
