from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import (
    DialogManager,
)

# from functions.clear_chat import clear_chat_window
from states.teacher_states import *
from states import StartState


class ExitToBot:

    @classmethod
    async def exit_to_bot(
        call: CallbackQuery, widget: Any, dialog_manager: DialogManager, *args, **kwargs
    ):
        # await clear_chat_window(call.message, call.bot)
        # await call.message.edit_text("Всего доброго! До следующей встречи.")
        await dialog_manager.switch_to(StartState.exit)
        # await dialog_manager.done()
        await call.answer("Всего доброго! До следующей встречи.")
