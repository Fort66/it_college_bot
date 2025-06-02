from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group
from aiogram_dialog.widgets.text import Const

from dialogs.class_TeacherDialog import TeacherDialog
from states.start_states import StartState


class StartDialog:
    dialog = Dialog(
        Window(
            Const("Привет! Я бот для принятия зачётов и экзаменов!\n\nᅠᅠᅠᅠᅠᅠВыберите свой профиль! 👇"),
            Group(
                Button(
                    Const("👨‍🏫 Преподаватель"),
                    id="teacher",
                    on_click=TeacherDialog.user,
                ),
                Button(Const("🧑🏻‍🎓 Студент"), id="student"),
                width=2,
            ),
            Cancel(Const("🔚 Выйти"), id="exit_to_bot"),
            state=StartState.start,
        ),
        Window(Const("Всего доброго! До следующей встречи."), state=StartState.exit),
    )
