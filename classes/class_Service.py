from typing import Any
from functools import partial
import re
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Group, Start, SwitchTo, Button, Back, Select, ScrollingGroup, Radio
from aiogram_dialog.widgets.text import Const, Format

import operator
from bot import bot
from database.class_Database import Database
from states.teacher_states import *
db = Database()



class Service:
    @staticmethod
    async def on_object_selected(
        sender,
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
    ):
        sender.item_id = item_id

    @staticmethod
    async def delete_object(
        sender,
        sender_state,
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        await db.delete_record(
            sender,
            field_name="id",
            id=int(sender.item_id),
        )
        await message.answer("Вопрос удалён", show_alert=True)
        sender.item_id = None
        await dialog_manager.switch_to(sender_state.start)