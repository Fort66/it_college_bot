from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards
from classes.class_SingleSelection import SingleSelection
from database.models import Groups

group_selection = SingleSelection()

group_router = Router()

db = Database()


@group_router.callback_query(F.data.startswith('groups'))
async def group_view(call: CallbackQuery, bot: Bot):
    groups = await db.get_table(Groups)

    # await call.message.delete()

    if groups:
        data = {}

        for group in groups:
            data[f"{group.id}"] = {
                "text": f"{group.name}",
                "callback_data": f"select_group_{group.id}",
            }

        kb = Keyboards(data=data)
        group_selection.data = data

        await call.message.edit_text(
            # chat_id=call.from_user.id,
            text=load_file("messages/teachers/groups/group_found"),
            reply_markup=await kb.inline_kb_generator(),
        )

        kb = Keyboards("keyboards/teachers/groups/what_doing")

        await bot.send_message(
            chat_id=call.from_user.id,
            text=load_file("messages/teachers/general/what_doing"),
            reply_markup=await kb.inline_kb_generator(2),
        )

    else:
        kb = Keyboards("keyboards/teachers/groups/groups")

        await call.message.edit_text(
            # chat_id=call.from_user.id,
            text=load_file("messages/teachers/groups/groups_not_found"),
            reply_markup=await kb.inline_kb_generator(2),
        )
    await call.answer(cache_time=1)