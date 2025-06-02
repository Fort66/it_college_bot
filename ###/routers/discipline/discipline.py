from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards
from classes.class_SingleSelection import SingleSelection

discipline_selection = SingleSelection()

discipline_router = Router()

db = Database()


@discipline_router.callback_query(F.data.startswith('disciplines'))
async def discipline_view(call: CallbackQuery, bot: Bot):
    disciplines = await db.get_disciplines(str(call.from_user.id))

    # await call.message.delete()

    if disciplines:
        data = {}

        for discipline in disciplines:
            data[f"{discipline.id}"] = {
                "text": f"{discipline.name}",
                "callback_data": f"select_discipline_{discipline.id}",
            }

        kb = Keyboards(data=data)
        discipline_selection.data = data

        await bot.edit_message_text(
            chat_id=call.from_user.id,
            text=load_file("messages/teachers/disciplines/discipline_found"),
            reply_markup=await kb.inline_kb_generator(),
        )

        kb = Keyboards("keyboards/teachers/disciplines/what_doing")

        await bot.send_message(
            chat_id=call.from_user.id,
            text=load_file("messages/teachers/general/what_doing"),
            reply_markup=await kb.inline_kb_generator(2),
        )

    else:
        kb = Keyboards("keyboards/teachers/disciplines/disciplines")

        await bot.edit_message_text(
            chat_id=call.from_user.id,
            text=load_file("messages/teachers/disciplines/disciplines_not_found"),
            reply_markup=await kb.inline_kb_generator(2),
        )
    await call.answer(cache_time=1)