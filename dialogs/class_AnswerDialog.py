from typing import Any
from functools import partial
import re
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window,
)
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Group, Start, SwitchTo, Button, Back, Select, ScrollingGroup, Radio, Multiselect
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State
import operator
from bot import bot

from database.class_Database import Database
from database.models import *
# from ..states.answers_stack import AnswersStack
from .class_TeacherDialog import TeacherDialog
from exit_to_bot.class_ExitToBot import ExitToBot
from functions.clear_chat import clear_chat_window
from classes.class_Service import Service

from states import *

db = Database()

answer_stack = AnswersStack()
from icecream import ic

class AnswerDialog:
    quest_id = None
    item_id = None
    def __init__(self):
        self.dialog = Dialog(
            Window(Format("Ответы на вопрос: {quest_text}"), self.paginated_answers(self.on_object_selected),
                Group(
                    Button(Const("🆕 Добавить ответ"), id="create_answer", on_click=partial(self.check_selected, id="create_answer")),

                    Button(Const("📝 Редактировать ответ"),id="edit_answer", on_click=partial(self.check_selected, id="edit_answer")),

                    Button(Const("🗑 Удалить ответ"), id="delete_answer", on_click=partial(self.check_selected, id="delete_answer")),

                    Button(Const("Все ответы"),id="create_answers", on_click=self.next_to_answer),
                    width=2,
                ),
                Cancel(Const("🔙 Вопросы")),
                state=AnswerState.start,
                getter=self.get_objects_list,
                parse_mode="HTML",
            ),

            Window(
                Const("Введите текст ответа.\nВнимание!!! Если тект предполагает вставку кода, то перед кодом\nоткройте теги <pre><code> и закройте теги </code></pre> после ввода кода."),
                TextInput(id="answer_text", on_success=partial(self.check_selected, id="create_answer")),
                state=AnswerState.create_answer,
            ),

            Window(
                Format("Введите измененный текст ответа.\nНе забывайте про теги, если в тексте вопроса должен быть код.\n\n<b>Вы редактируете ответ:</b>\n\n{answer_text}"),
                TextInput(id="edit_answer_text", on_success=partial(self.check_selected, id="edit_answer")),
                SwitchTo(Const("Отменить"), id="cancel_edit", state=AnswerState.start),
                state=AnswerState.edit_answer,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),

            Window(
                Const("Этот правильный ответ на вопрос? Да - 1, Нет - 0"),
                TextInput(id="is_correct", on_success=self.is_correct_handler),
                state=AnswerState.is_correct,
                ),

            Window(
                Format("Вы собираетесь удалить ответ:\n\n{answer_text}\n\nВы уверены?"),
                Group(
                    Button(Const("Удалить"), id="delete", on_click=self.delete_object),
                    SwitchTo(Const("Отмена"), id="cancel", state=QuestionState.start),
                    width=2,
                ),
                state=AnswerState.is_delete,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),
        )

    @staticmethod
    async def is_correct_handler(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        data: str
    ):
        ctx = dialog_manager.current_context()
        if ctx.widget_data.get("answer_text"):
            ctx.dialog_data["answer_is_correct"] = data
            await AnswerDialog.check_selected(message, widget, dialog_manager, id="create_answer")
        elif ctx.widget_data.get("edit_answer_text"):
            ctx.dialog_data["answer_is_correct"] = data
            await AnswerDialog.check_selected(message, widget, dialog_manager, id="edit_answer")

    @classmethod
    async def on_object_selected(
        cls,
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
    ):
        cls.item_id = item_id

    @staticmethod
    async def check_selected(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):

        if AnswerDialog.item_id is None and kwargs["id"] != "create_answer":
            await message.answer("Выберите ответ", show_alert=True)
            return False
        else:
            match kwargs["id"]:
                case "create_answer":
                    ctx = dialog_manager.current_context()

                    if not ctx.widget_data.get("answer_text"):
                        await dialog_manager.switch_to(AnswerState.create_answer)

                    elif not dialog_manager.dialog_data.get("answer_is_correct"):
                        await dialog_manager.switch_to(AnswerState.is_correct)

                    elif ctx.widget_data.get("answer_text") and dialog_manager.dialog_data.get("answer_is_correct"):
                        await AnswerDialog.create_object(message, widget, dialog_manager, AnswerDialog.item_id)
                        ctx.widget_data["answer_text"] = None
                        ctx.dialog_data["answer_is_correct"] = None

                case "edit_answer":
                    ctx = dialog_manager.current_context()
                    if not ctx.widget_data.get("edit_answer_text"):
                        await dialog_manager.switch_to(AnswerState.edit_answer)

                    elif not dialog_manager.dialog_data.get("answer_is_correct"):
                            await dialog_manager.switch_to(AnswerState.is_correct)

                    elif ctx.widget_data.get("edit_answer_text") and dialog_manager.dialog_data.get("answer_is_correct"):
                        await AnswerDialog.edit_object(message, widget, dialog_manager, AnswerDialog.item_id)
                        ctx.widget_data["answer_text"] = None
                        ctx.dialog_data["answer_is_correct"] = None
                case "delete_answer":
                    await dialog_manager.switch_to(AnswerState.is_delete)


    @staticmethod
    async def next_to_answer(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        **kwargs
        ):
        if AnswerDialog.item_id:
            await dialog_manager.start(AnswerState.start, data=AnswerDialog.item_id)
        else:
            await message.answer("Выберите ответ", show_alert=True)

    @staticmethod
    async def edit_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        ctx = dialog_manager.current_context()
        try:
            await db.update_record(
                Answers,
                field_name="id",
                id=int(AnswerDialog.item_id),
                text=ctx.widget_data["edit_answer_text"],
                is_correct=int(ctx.dialog_data["answer_is_correct"]),
            )
            await clear_chat_window(message, dialog_manager.event.bot)
            await dialog_manager.switch_to(AnswerState.start)
        except Exception as e:
            print(e)

    @staticmethod
    async def create_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        data: str
    ):
        ctx = dialog_manager.current_context()
        await Database().add_record(
            Answers,
            object_id=AnswerDialog.quest_id,
            text=ctx.widget_data["answer_text"],
            is_correct=int(ctx.dialog_data["answer_is_correct"])
        )
        await clear_chat_window(message, dialog_manager.event.bot)
        await dialog_manager.switch_to(AnswerState.start)

    @staticmethod
    async def delete_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        await db.delete_record(
            Answers,
            field_name="id",
            id=int(AnswerDialog.item_id),
        )
        await message.answer("Ответ удалён", show_alert=True)
        AnswerDialog.item_id = None
        await dialog_manager.switch_to(AnswerState.start)

    @staticmethod
    async def get_objects_list(dialog_manager: DialogManager, **kwargs):
        AnswerDialog.quest_id = int(dialog_manager.start_data)
        quest = await db.get_record(
            Quests,
            field_name="id",
            id = AnswerDialog.quest_id,
        )
        object_list = []
        answers = await db.get_records(Answers, field_name="object_id", object_id=int(dialog_manager.start_data))

        for answer in answers:
            object_list.append((f"{'🔹' if answer.is_correct else ''}{answer.text}", answer.id))

        data = {
            "quest_text": quest.text,
            "answers": object_list
        }
        return data

    @staticmethod
    async def get_object_one(dialog_manager: DialogManager, *args, **kwargs):
        answer = await db.get_record(
            Answers,
            field_name="id",
            id=int(AnswerDialog.item_id),
        )
        return {"answer_text": answer.text}

    @staticmethod
    def paginated_answers(on_click):
        return ScrollingGroup(
            Radio(
                Format("✅ {item[0]}"),
                Format("ᅠᅠ{item[0]}"),
                id="s_scroll_answers",
                item_id_getter=operator.itemgetter(1),
                items="answers",
                on_click=on_click,
            ),
            id="answers_id",
            width=1, height=5,
        )
