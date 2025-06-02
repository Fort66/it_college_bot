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
from aiogram_dialog.widgets.text import Const, Format, Jinja

import operator
from bot import bot

from database.class_Database import Database
from database.models import *
from .class_TeacherDialog import TeacherDialog
from exit_to_bot.class_ExitToBot import ExitToBot
from functions.clear_chat import clear_chat_window
from classes.class_Service import Service

from states.teacher_states import *

db = Database()


# from keyboards.keyboards import paginated_questions
from icecream import ic

class QuestDialog:
    discipline_id = None
    item_id = None
    def __init__(self):
        self.dialog = Dialog(
            Window(Format("<b>Вопросы по предмету:</b>\n{discipline_text}"), self.paginated_questions(self.on_object_selected),
                Group(
                    SwitchTo(Const("🆕 Добавить вопрос"), id="create_quest", state=QuestionState.create_quest),

                    Button(Const("📝 Редактировать вопрос"),id="edit_quest", on_click=partial(self.check_selected, id="edit_quest")),

                    Button(Const("🗑 Удалить вопрос"), id="delete_quest", on_click=partial(self.check_selected, id="delete_quest")),

                    Button(Const("Ответы к вопросу"),id="next_to_answers", on_click=self.next_to_answer),
                    width=2,
                ),
                Cancel(Const("🔙 Предметы")),
                state=QuestionState.start,
                getter=self.get_objects_list,
                parse_mode="HTML",
            ),

            Window(
                Const("Введите текст вопроса.\nВнимание!!! Если тект предполагает вставку кода, то перед кодом\nоткройте теги <pre><code> и закройте теги </code></pre> после ввода кода"),
                TextInput(id="quest_text", on_success=self.create_object),
                state=QuestionState.create_quest,
            ),

            Window(
                Format("Введите измененный текст вопроса.\nНе забывайте про теги, если в тексте вопроса должен быть код\n\n<b>Вы редактируете вопрос:</b>\n\n{quest_text}"),
                TextInput(id="edit_quest_text", on_success=self.edit_object),
                SwitchTo(Const("Отменить"), id="cancel_edit", state=QuestionState.start),
                state=QuestionState.edit_quest,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),

            Window(
                Format("Вы собираетесь удалить вопрос:\n\n{quest_text}\n\nВы уверены?"),
                Group(
                    Button(Const("Удалить"), id="delete", on_click=self.delete_object),
                    SwitchTo(Const("Отмена"), id="cancel", state=QuestionState.start),
                    width=2,
                ),
                state=QuestionState.is_delete,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),
        )

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
        # ic(dialog_manager.dialog_data)
        # ic(dialog_manager.current_context())
        if QuestDialog.item_id is None:
            await message.answer("Выберите вопрос", show_alert=True)
            return False
        else:
            match kwargs["id"]:
                case "edit_quest":
                    await dialog_manager.switch_to(QuestionState.edit_quest)
                case "delete_quest":
                    await dialog_manager.switch_to(QuestionState.is_delete)

    @staticmethod
    async def next_to_answer(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        **kwargs
        ):
        if QuestDialog.item_id:
            await dialog_manager.start(AnswerState.start, data=QuestDialog.item_id)
        else:
            await message.answer("Выберите вопрос", show_alert=True)

    @staticmethod
    async def edit_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        if args:
            text = args[0]
            try:
                await db.update_record(
                    Quests,
                    field_name="id",
                    id=int(QuestDialog.item_id),
                    text=f"{text}",
                )
                await clear_chat_window(message, dialog_manager.event.bot)
                await dialog_manager.switch_to(QuestionState.start)
            except Exception as e:
                print(e)

    @staticmethod
    async def create_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        data: str
    ):

        text = data
        await Database().add_record(
            Quests,
            object_id=QuestDialog.discipline_id,
            text=text,
        )
        await clear_chat_window(message, dialog_manager.event.bot)
        await dialog_manager.switch_to(QuestionState.start)

    @staticmethod
    async def delete_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        await db.delete_record(
            Quests,
            field_name="id",
            id=int(QuestDialog.item_id),
        )
        await message.answer("Вопрос удалён", show_alert=True)
        QuestDialog.item_id = None
        await dialog_manager.switch_to(QuestionState.start)

    @staticmethod
    async def get_objects_list(dialog_manager: DialogManager, **kwargs):
        QuestDialog.discipline_id = int(dialog_manager.start_data)
        discipline = await db.get_record(
            Disciplines,
            field_name="id",
            id = QuestDialog.discipline_id,
        )
        # discipline = Jinja(discipline.text)
        object_list = []
        questions = await db.get_records(Quests, field_name="object_id", object_id=int(dialog_manager.start_data))

        for quest in questions:
            answer_amount = len(await db.get_records(Answers, field_name="object_id", object_id=quest.id))
            object_list.append((f"({answer_amount}) {quest.text} ", quest.id))

        data = {
            "discipline_text": discipline.text,
            "questions": object_list
        }
        return data

    @staticmethod
    async def get_object_one(dialog_manager: DialogManager, *args, **kwargs):
        question = await db.get_record(
            Quests,
            field_name="id",
            id=int(QuestDialog.item_id),
        )
        return {"quest_text": question.text}

    @staticmethod
    def paginated_questions(on_click):
        return ScrollingGroup(
            Radio(
                Format("✅ {item[0]}"),
                Format("ᅠᅠ{item[0]}"),
                id="s_scroll_questions",
                item_id_getter=operator.itemgetter(1),
                items="questions",
                on_click=on_click,
            ),
            id="questions_id",
            width=1, height=10,
        )