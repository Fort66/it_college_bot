from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from database.class_Database import Database
from states.other_states import StudentState

import re

from keyboards.class_Keyboards import Keyboards

from functions.load_json_file import load_file

student_router = Router()


# @student_router.callback_query(F.data == load_file('keyboards/general/profile', True)['student']['callback_data'])
# async def teacher(call: CallbackQuery, state: FSMContext, bot: Bot):
#     await state.clear()
#     db = Database()
#     await call.answer()
#     await call.message.delete()
#     await state.set_state(TeacherState.name)
#     await call.message.answer(load_file('messages_texts/check_access_to_profile', True)['check_access'])

# @student_router.message(TeacherState.name)
# async def check_access(message: Message, state: FSMContext, bot: Bot):
#     db = Database()