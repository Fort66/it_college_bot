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


class GroupsDialog:
    item_id = None

    def __init__(self):
        self.dialog = Dialog(
            Window(
                Const("<b>Ваши группы</b>"),
                self.paginated_groups(self.on_object_selected),
                Group(
                    SwitchTo(
                        Const("🆕 Добавить группу"),
                        id="create_group",
                        state=GroupState.create_group,
                    ),

                    Button(
                        Const("📝 Редактировать группу"),
                        id="edit_group",
                        on_click=partial(self.check_selected, id="edit_group"),
                    ),

                    Button(
                        Const("🗑 Удалить группу"),
                        id="delete_group",
                        on_click=partial(self.check_selected, id="delete_group"),
                    ),

                    Button(
                        Const("📃 Список студентов"),
                        id="next_to_studens_list",
                        on_click=self.next_to_students_list,
                    ),

                    Cancel(Const("🔙 Меню преподавателя")),
                    width=2,
                ),
                state=GroupState.start,
                getter=self.get_objects_list,
                parse_mode="HTML",
            ),

            Window(
                Const(
                    "Введите название группы"
                ),
                TextInput(id="group_text", on_success=self.create_object),
                state=GroupState.create_group,
            ),

            Window(
                Format(
                    "Введите изменённое название группы\n\n<b>Вы редактируете группу:</b>\n\n{group_text}"),
                TextInput(id="edit_group_text", on_success=self.edit_object),

                SwitchTo(Const("Отменить"), id="cancel_edit", state=GroupState.start),
                state=GroupState.edit_group,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),

            Window(
                Format("Вы собираетесь удалить группу:\n\n{group_text}\n\nВы уверены?"),
                Group(
                    Button(Const("Удалить"), id="delete", on_click=self.delete_object),

                    SwitchTo(Const("Отмена"), id="cancel", state=GroupState.start),
                    width=2,
                ),
                state=GroupState.is_delete,
                getter=self.get_object_one,
                parse_mode="HTML",
            ),
        )

    @staticmethod
    async def next_to_students_list(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager
    ):
        if GroupsDialog.item_id:
            await dialog_manager.start(StudentListState.start, data=GroupsDialog.item_id)
        else:
            await message.answer("Выберите группу", show_alert=True)

    @staticmethod
    async def on_object_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
    ):
        GroupsDialog.item_id = item_id

    @staticmethod
    async def check_selected(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        if GroupsDialog.item_id is None:
            await message.answer("Выберите группу", show_alert=True)
            return False
        else:
            match kwargs["id"]:
                case "edit_group":
                    await dialog_manager.switch_to(GroupState.edit_group)
                case "delete_group":
                    await dialog_manager.switch_to(GroupState.is_delete)

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
                    Groups,
                    field_name="id",
                    id=int(GroupsDialog.item_id),
                    text=args[0],
                )
                await clear_chat_window(message, dialog_manager.event.bot)
                await dialog_manager.switch_to(GroupState.start)
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
            Groups,
            object_id=message.from_user.id,
            text=name,
        )
        await clear_chat_window(message, dialog_manager.event.bot)
        await dialog_manager.switch_to(GroupState.start)


    @staticmethod
    async def delete_object(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        await db.delete_record(
            Groups,
            field_name="id",
            id=int(GroupsDialog.item_id),
        )
        await message.answer("Группа удалена", show_alert=True)
        GroupsDialog.item_id = None
        await dialog_manager.switch_to(GroupState.start)

    @staticmethod
    async def get_objects_list(dialog_manager: DialogManager, **kwargs):
        groups = await db.get_records(
            Groups,
            field_name="object_id",
            object_id=dialog_manager.event.from_user.id,
        )

        object_list = []
        for group in groups:
            quest_amount = len(await db.get_records(Groups, field_name="object_id", object_id=group.id))
            object_list.append((f"{group.text} ", group.id))

        data = {
            "groups": object_list
        }
        return data

    @staticmethod
    async def get_object_one(dialog_manager: DialogManager, *args, **kwargs):
        group = await db.get_record(
            Groups,
            field_name="id",
            id=int(GroupsDialog.item_id),
        )
        return {"group_text": group.text}

    @staticmethod
    def paginated_groups(on_click):
        return ScrollingGroup(
            Radio(
                Format("✅ {item[0]}"),
                Format("ᅠᅠ{item[0]}"),
                id="s_scroll_groups",
                item_id_getter=operator.itemgetter(1),
                items="groups",
                on_click=on_click,
            ),
            id="groups_id",
            width=1,
            height=10,
        )
