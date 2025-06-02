from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards

from states.other_states import GroupState
from routers.group.select_group import group_selection


create_group_router = Router()


@create_group_router.callback_query(or_f(F.data.startswith("create_group"),F.data.startswith("edit_group")))
async def create_group(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=load_file("messages/teachers/groups/add_group_name"),
        reply_markup=None,
    )

    await state.set_state(GroupState.name)

    await call.answer()

@create_group_router.message(GroupState.name)
async def create_group_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=message.text)

    group = await state.get_data()

    db = Database()

    if group_selection.value is None:
        await db.add_group(
            name=group["name"],
        )
    else:
        await db.update_group(
            group_id=group_selection.value,
            name=group["name"],
        )

    kb = Keyboards("keyboards/teachers/general/main")

    await clear_chat(message, bot)

    await bot.send_message(
        chat_id=message.chat.id,
        text=load_file("messages/teachers/groups/group_success"),
        reply_markup=await kb.inline_kb_generator(2),
    )
    await clear_chat(message, bot)
    await state.clear()
