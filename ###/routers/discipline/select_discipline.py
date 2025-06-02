from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards

from routers.discipline.discipline import discipline_selection

select_discipline_router = Router()


@select_discipline_router.callback_query(F.data.startswith("select_discipline"))
async def create_discipline(call: CallbackQuery, bot: Bot):
    discipline_id = call.data.split("_")[-1]

    discipline_selection.value = discipline_id

    await call.answer()

    for value in discipline_selection.data.keys():
        if value == discipline_id and discipline_selection.data[value]["text"].startswith("✅"):
            discipline_selection.value = None
            discipline_selection.data[value]["text"] = discipline_selection.data[
                value
            ]["text"].replace("✅", "")

        elif value == discipline_id and not discipline_selection.data[value]["text"].startswith("✅"):
            discipline_selection.value = discipline_id
            discipline_selection.data[value]["text"] = (
                f"✅{discipline_selection.data[value]['text']}"
            )

        elif value != discipline_id and discipline_selection.data[value]["text"].startswith("✅"):
            discipline_selection.value = None
            discipline_selection.data[value]["text"] = discipline_selection.data[value]["text"].replace("✅", "")

    kb = Keyboards(data=discipline_selection.data)
    await call.message.edit_reply_markup(
        reply_markup=await kb.inline_kb_generator()
    )
