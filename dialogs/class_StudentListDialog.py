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


class StudentListDialog:
    group_id = None
    item_id = None

    def __init__(self):
        self.dialog = Dialog(
            Window(
                Const("<b>Список студентов группы</b>"),
                self.paginated_students_list(self.on_object_selected),
                Group(
                    SwitchTo(
                        Const("🆕 Добавить студента"),
                        id="create_student",
                        state=StudentListState.create_student,
                    ),

                    Button(
                        Const("📝 Редактировать студента"),
                        id="edit_student",
                        on_click=partial(self.check_selected, id="edit_student"),
                    ),

                    Button(
                        Const("🗑 Удалить студента"),
                        id="delete_student",
                        on_click=partial(self.check_selected, id="delete_student"),
                    ),

                    Cancel(Const("🔙 Группы")),
                    width=2,
                ),
                state=StudentListState.start,
                getter=self.get_objects_list,
                parse_mode="HTML",
            ),

            Window(
                Const(
                    "Введите ФИО студента"
                ),
                TextInput(id="student_text", on_success=self.create_object),
                state=StudentListState.create_student,
            ),

            Window(
                Format(
                    "Введите изменённое ФИО\n\n<b>Вы редактируете студента:</b>\n\n{student_text}"),
                TextInput(id="edit_student_text", on_success=self.edit_object),

                SwitchTo(Const("Отменить"), id="cancel_edit", state=StudentListState.start),
                state=StudentListState.edit_student,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),

            Window(
                Format("Вы собираетесь удалить студента:\n\n{student_text}\n\nВы уверены?"),
                Group(
                    Button(Const("Удалить"), id="delete", on_click=self.delete_object),

                    SwitchTo(Const("Отмена"), id="cancel", state=StudentListState.start),
                    width=2,
                ),
                state=StudentListState.is_delete,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),
        )

    @staticmethod
    async def on_object_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
    ):
        StudentListDialog.item_id = item_id

    @staticmethod
    async def check_selected(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        if StudentListDialog.item_id is None:
            await message.answer("Выберите студента", show_alert=True)
            return False
        else:
            match kwargs["id"]:
                case "edit_student":
                    await dialog_manager.switch_to(StudentListState.edit_student)
                case "delete_student":
                    await dialog_manager.switch_to(StudentListState.is_delete)

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
                    Students,
                    field_name="id",
                    id=int(StudentListDialog.item_id),
                    text=args[0],
                )
                await clear_chat_window(message, dialog_manager.event.bot)
                await dialog_manager.switch_to(StudentListState.start)
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
            Students,
            object_id=StudentListDialog.group_id,
            text=text,
        )
        await clear_chat_window(message, dialog_manager.event.bot)
        await dialog_manager.switch_to(StudentListState.start)


    @staticmethod
    async def delete_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        await db.delete_record(
            Students,
            field_name="id",
            id=int(StudentListDialog.item_id),
        )
        await message.answer("Студент удалён", show_alert=True)
        StudentListDialog.item_id = None
        await dialog_manager.switch_to(StudentListState.start)

    @staticmethod
    async def get_objects_list(dialog_manager: DialogManager, **kwargs):
        StudentListDialog.group_id = int(dialog_manager.start_data)
        students = await db.get_records(
            Students,
            field_name="object_id",
            object_id=StudentListDialog.group_id,
        )

        object_list = []
        for student in students:
            # quest_amount = len(await db.get_records(Groups, field_name="object_id", object_id=group.id))
            object_list.append((f"{student.text} ", student.id))

        data = {
            "students": object_list
        }
        return data

    @staticmethod
    async def get_object_one(dialog_manager: DialogManager, *args, **kwargs):
        student = await db.get_record(
            Students,
            field_name="id",
            id=int(StudentListDialog.item_id),
        )
        return {"student_text": student.text}

    @staticmethod
    def paginated_students_list(on_click):
        return ScrollingGroup(
            Radio(
                Format("✅ {item[0]}"),
                Format("ᅠᅠ{item[0]}"),
                id="s_scroll_students",
                item_id_getter=operator.itemgetter(1),
                items="students",
                on_click=on_click,
            ),
            id="students_id",
            width=1,
            height=10,
        )
