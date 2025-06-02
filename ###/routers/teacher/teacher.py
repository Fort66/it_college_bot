import asyncio
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from email_validator import EmailNotValidError, validate_email
from icecream import ic

from database.class_Database import Database
from functions.clear_chat import clear_chat
from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards
from states.other_states import TeacherState

teacher_router = Router()

db = Database()


@teacher_router.callback_query(F.data == "teacher")
async def teacher(call: CallbackQuery, state: FSMContext, bot: Bot):
    # await state.clear()
    # await call.message.delete()
    reg_complete = await db.get_teacher_id(str(call.from_user.id))

    if reg_complete is not None:
        kb = Keyboards("keyboards/teachers/general/main")

        await call.message.edit_text(
            text=f"{load_file('messages/teachers/general/access_open')} {reg_complete.name}!",
            reply_markup=await kb.inline_kb_generator(2),
        )

    else:
        await call.message.edit_text(
            load_file("messages/teachers/general/check_access_to_profile")
        )
        await state.set_state(TeacherState.name)

    await call.answer()


@teacher_router.message(TeacherState.name)
async def input_name(message: Message, state: FSMContext, bot: Bot):
    result = await db.get_teacher_name(message.text)

    if not result:
        await state.clear()

        await bot.edit_message_text(
            message.chat.id, load_file("messages/teachers/reg/not_found")
        )

    else:
        await bot.edit_message_text(
            message.chat.id, load_file("messages/teachers/reg/found")
        )

        await state.update_data(name=message.text)

        await state.set_state(TeacherState.email)


@teacher_router.message(TeacherState.email)
async def input_email(message: Message, state: FSMContext, bot: Bot):
    try:
        validate_email(message.text)

        await state.update_data(email=message.text)

        reg_data = await state.get_data()

        db = Database()

        await db.update_teacher(
            name=reg_data["name"],
            telegram_id=str(message.from_user.id),
            telegram_name=message.from_user.username,
            email=reg_data["email"],
        )

        await state.clear()

        await clear_chat(message, bot)

        kb = Keyboards("keyboards/teachers/general/main")

        # await bot.send_message(
        #     message.from_user.id,
        #     load_file("messages/teachers/reg/enter_email"),
        #     reply_markup=kb.reply_kb_generator_from_json(2),
        # )
        reg_msg = await bot.edit_message_text(
            message.from_user.id,
            load_file("messages/teachers/reg/enter_email")
        )
        await asyncio.sleep(2)
        await bot.delete_message(message.from_user.id, reg_msg.message_id)

        data = {}

        await bot.edit_message_text(
            message.from_user.id,
            "С чем будем работать?",
            reply_markup=await kb.inline_kb_generator(2),
        )


    except EmailNotValidError as e:
        await bot.edit_message_text(
            message.from_user.id, load_file("messages/teachers/reg/email_error")
        )
