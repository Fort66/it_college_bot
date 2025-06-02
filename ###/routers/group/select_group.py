from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards

from routers.group.group import group_selection

select_group_router = Router()


@select_group_router.callback_query(F.data.startswith("select_group"))
async def create_group(call: CallbackQuery, bot: Bot):
    group_id = call.data.split("_")[-1]

    group_selection.value = group_id

    await call.answer()

    for value in group_selection.data.keys():
        if value == group_id and group_selection.data[value]["text"].startswith("✅"):
            group_selection.value = None
            group_selection.data[value]["text"] = group_selection.data[
                value
            ]["text"].replace("✅", "")

        elif value == group_id and not group_selection.data[value]["text"].startswith("✅"):
            group_selection.value = group_id
            group_selection.data[value]["text"] = (
                f"✅{group_selection.data[value]['text']}"
            )

        elif value != group_id and group_selection.data[value]["text"].startswith("✅"):
            group_selection.value = None
            group_selection.data[value]["text"] = group_selection.data[value]["text"].replace("✅", "")

    kb = Keyboards(data=group_selection.data)
    await call.message.edit_reply_markup(
        reply_markup=await kb.inline_kb_generator()
    )
