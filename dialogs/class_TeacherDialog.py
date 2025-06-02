from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Group, Start, SwitchTo
from aiogram_dialog.widgets.text import Const

from database.class_Database import Database
from database.models import *
from functions.clear_chat import clear_chat_window
from states.teacher_states import *

db = Database()


class TeacherDialog:
    id = None

    def __init__(self):
        self.dialog = Dialog(
            Window(
                Const(
                    "ᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠУпс 😧\nНе нахожу Вас в списке зарегистрированных преподавателей.\nВозможно Вас нет в базе, или процесс регистрации не завершён.\nВведите, пожалуйста, свои имя, отчество и фамилию в формате:\nᅠᅠᅠᅠᅠᅠᅠᅠ👉 Имя Отчество Фамилия 👈\nи я проверю Вас по базе данных! 🕵🏻‍♂️"
                    ),
                TextInput(
                    id="input_teacher_name",
                    on_success=self.get_name,
                ),
                state=TeacherState.name,
            ),
            Window(
                Const(
                    "Да, Вы есть в базе данных!\nНо процесс Вашей регистрации не завершен.\nДавайте завершим его. От Вас потребуется некоторая информация.\nВведите, пожалуйста, свой email"
                    ),
                TextInput(id="input_teacher_email", on_success=self.update_user),
                state=TeacherState.email,
            ),
            Window(
                Const(
                    "Спасибо! Ваши данные успешно сохранены!"
                    ),
                SwitchTo(
                    Const("Меню преподавателя ▶️"),
                    id="is_teacher",
                    state=TeacherState.is_registry,
                ),
                Cancel(Const("🔚 Выйти из бота"), id="exit_to_bot"),
                state=TeacherState.success_registry,
            ),
            Window(
                Const("Приветствую!"),
                Group(
                    Start(
                        Const("📚 Предметы"),
                        id="disciplines",
                        state=DisciplineState.start,
                    ),
                    Start(Const("👩🏼‍🎓👨🏻‍🎓 Группы"), id="groups", state=GroupState.start),
                    Start(
                        Const("‼️ Экзамены / Зачеты"), id="exam", state=ExamState.start
                    ),
                    Cancel(Const("🔙 Профили"), id="exit_to_bot"),
                    width=2,
                ),
                state=TeacherState.is_registry,
            ),
            Window(
                Const(
                    "Извините, но Вас нет в базе данных пользователей! Для добавления в базу, обратитесь  к главному администратору!"
                ),
                state=TeacherState.not_found,
            ),
        )

    @staticmethod
    async def user(
        call: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        reg_complete = await db.get_record(
            Teachers, field_name="user_id", user_id=str(call.from_user.id)
        )

        if reg_complete is None:
            await dialog_manager.start(
                TeacherState.name, data=dialog_manager.dialog_data
            )
        else:
            await dialog_manager.start(
                TeacherState.is_registry, data=dialog_manager.dialog_data
            )

    @staticmethod
    async def is_user(
        call: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        *args,
        **kwargs,
    ):
        match kwargs["id"]:
            case "is_teacher":
                await dialog_manager.switch_to(TeacherState.is_registry)

    @staticmethod
    async def get_name(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        data: str,
        *args,
        **kwargs,
    ):
        dialog_manager.dialog_data["text"] = data
        dialog_manager.dialog_data["user_id"] = dialog_manager.event.from_user.id
        dialog_manager.dialog_data["username"] = dialog_manager.event.from_user.username

        result = await db.get_record(Teachers, field_name="text", text=data)

        if result is not None:
            dialog_manager.dialog_data["id"] = result.id
            await clear_chat_window(message, dialog_manager.event.bot)
            await dialog_manager.switch_to(TeacherState.email)
        else:
            await dialog_manager.done()
            await dialog_manager.done()
            await clear_chat_window(message, dialog_manager.event.bot)
            (
                await message.answer(
                    "Извините, но Вас нет в базе данных пользователей! Для добавления в базу, обратитесь  к главному администратору!"
                ),
            )

    @staticmethod
    async def update_user(
        message: Message,
        widget: TextInput,
        dialog_manager: DialogManager,
        data: str,
        *args,
        **kwargs,
    ):
        db = Database()
        dialog_manager.dialog_data["email"] = data
        await clear_chat_window(message, dialog_manager.event.bot)

        try:
            await db.update_record(
                Teachers,
                field_name="id",
                id=dialog_manager.dialog_data["id"],
                user_id=dialog_manager.dialog_data["user_id"],
                text=dialog_manager.dialog_data["text"],
                username=dialog_manager.dialog_data["username"],
                email=dialog_manager.dialog_data["email"],
            )
            await dialog_manager.switch_to(TeacherState.success_registry)
        except Exception as e:
            print(e)
