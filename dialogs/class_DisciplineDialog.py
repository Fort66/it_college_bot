import operator
from functools import partial
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Group,
    Radio,
    ScrollingGroup,
    SwitchTo,
    Back
)
from aiogram_dialog.widgets.text import Const, Format

from database.class_Database import Database
from database.models import *
from functions.clear_chat import clear_chat_window
from states.teacher_states import *

from classes.class_Service import Service
from icecream import ic
from bot import bot
db = Database()


class DisciplineDialog:
    item_id = None

    def __init__(self):
        self.dialog = Dialog(
            Window(
                Const("<b>Ваши предметы</b>"),
                self.paginated_disciplines(self.on_object_selected),
                Group(
                    SwitchTo(
                        Const("🆕 Добавить предмет"),
                        id="create_discipline",
                        state=DisciplineState.create_discipline,
                    ),

                    Button(
                        Const("📝 Редактировать предмет"),
                        id="edit_discipline",
                        on_click=partial(self.check_selected, id="edit_discipline"),
                    ),

                    Button(
                        Const("🗑 Удалить предмет"),
                        id="delete_discipline",
                        on_click=partial(self.check_selected, id="delete_discipline"),
                    ),

                    Button(
                        Const("❓ Вопросы / Ответы"),
                        id="next_to_questions",
                        on_click=self.next_to_quest,
                    ),

                    Cancel(Const("🔙 Меню преподавателя")),
                    width=2,
                ),
                state=DisciplineState.start,
                getter=self.get_objects_list,
                parse_mode="HTML",
            ),

            Window(
                Const(
                    "Введите название предмета"
                ),
                TextInput(id="discipline_text", on_success=self.create_object),
                state=DisciplineState.create_discipline,
            ),

            Window(
                Format(
                    "Введите изменённое название предмета\n\n<b>Вы редактируете предмет:</b>\n\n{discipline_text}"),
                TextInput(id="edit_discipline_text", on_success=self.edit_object),

                SwitchTo(Const("Отменить"), id="cancel_edit", state=DisciplineState.start),
                state=DisciplineState.edit_discipline,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),

            Window(
                Format("Вы собираетесь удалить предмет:\n\n{discipline_text}\n\nВы уверены?"),
                Group(
                    Button(Const("Удалить"), id="delete", on_click=self.delete_object),

                    SwitchTo(Const("Отмена"), id="cancel", state=DisciplineState.start),
                    width=2,
                ),
                state=DisciplineState.is_delete,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),
        )

    @staticmethod
    async def next_to_quest(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager
    ):
        if DisciplineDialog.item_id:
            await dialog_manager.start(QuestionState.start, data=DisciplineDialog.item_id)
        else:
            await message.answer("Выберите предмет", show_alert=True)

    @staticmethod
    async def on_object_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
    ):
        DisciplineDialog.item_id = item_id

    @staticmethod
    async def check_selected(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        if DisciplineDialog.item_id is None:
            await message.answer("Выберите предмет", show_alert=True)
            return False
        else:
            match kwargs["id"]:
                case "edit_discipline":
                    await dialog_manager.switch_to(DisciplineState.edit_discipline)
                case "delete_discipline":
                    await dialog_manager.switch_to(DisciplineState.is_delete)

    @staticmethod
    async def edit_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        if args:
            try:
                await db.update_record(
                    Disciplines,
                    field_name="id",
                    id=int(DisciplineDialog.item_id),
                    text=args[0],
                )
                await clear_chat_window(message, dialog_manager.event.bot)
                await dialog_manager.switch_to(DisciplineState.start)
            except Exception as e:
                print(e)

    @staticmethod
    async def create_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        data: str
    ):

        name = data
        await Database().add_record(
            Disciplines,
            object_id=message.from_user.id,
            text=name,
        )
        await clear_chat_window(message, dialog_manager.event.bot)
        await dialog_manager.switch_to(DisciplineState.start)


    @staticmethod
    async def delete_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        await db.delete_record(
            Disciplines,
            field_name="id",
            id=int(DisciplineDialog.item_id),
        )
        await message.answer("Предмет удалён", show_alert=True)
        DisciplineDialog.item_id = None
        await dialog_manager.switch_to(DisciplineState.start)

    @staticmethod
    async def get_objects_list(dialog_manager: DialogManager, **kwargs):
        disciplines = await db.get_records(
            Disciplines,
            field_name="object_id",
            object_id=dialog_manager.event.from_user.id,
        )

        object_list = []
        for discipline in disciplines:
            quest_amount = len(await db.get_records(Quests, field_name="object_id", object_id=discipline.id))
            object_list.append((f"({quest_amount}) {discipline.text} ", discipline.id))

        data = {
            "disciplines": object_list
        }
        return data

    @staticmethod
    async def get_object_one(dialog_manager: DialogManager, *args, **kwargs):
        discipline = await db.get_record(
            Disciplines,
            field_name="id",
            id=int(DisciplineDialog.item_id),
        )
        return {"discipline_text": discipline.text}

    @staticmethod
    def paginated_disciplines(on_click):
        return ScrollingGroup(
            Radio(
                Format("✅ {item[0]}"),
                Format("ᅠᅠ{item[0]}"),
                id="s_scroll_disciplines",
                item_id_getter=operator.itemgetter(1),
                items="disciplines",
                on_click=on_click,
            ),
            id="disciplines_id",
            width=1,
            height=10,
        )
