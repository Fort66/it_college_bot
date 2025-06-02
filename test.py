# from aiogram import Bot, Dispatcher
# from aiogram.enums import ParseMode
# from aiogram_dialog import Dialog, DialogManager, StartMode, Window
# from aiogram_dialog.widgets.kbd import Button, Row
# from aiogram_dialog.widgets.text import Format
# from aiogram.types import Message
# from aiogram.fsm.storage.memory import MemoryStorage

# # ===== Состояния =====
# from enum import Enum

# class States(Enum):
#     MAIN = "main"
#     INFO = "info"

# # ====== Код бота ======

# bot = Bot("7205076132:AAHS4bKNtfg3gD3PB7iHsszj1ZEH9rnYVtU")
# storage = MemoryStorage()
# dp = Dispatcher(storage=storage)

# # ====== Диалог ======
# dialog = Dialog(
#     Window(
#         Format("<b>Добро пожаловать!</b>\n\nВыберите действие ниже 👇"),  # <-- HTML-форматирование
#         Row(
#             Button(text="🔹 О программе", id="btn_info", on_click=lambda c, b: c.dialog_manager.switch_to(States.INFO)),
#             Button(text="⚙️ Настройки", id="btn_settings"),
#         ),
#         state=States.MAIN,
#         parse_mode=ParseMode.HTML,  # <-- важно!
#     ),
#     Window(
#         Format("<i>Это демо-пример работы aiogram_dialog с HTML-разметкой.</i>\n\nНажмите Назад для возврата."),
#         Row(
#             Button(text="⬅️ Назад", id="btn_back", on_click=lambda c, b: c.dialog_manager.switch_to(States.MAIN)),
#         ),
#         state=States.INFO,
#         parse_mode=ParseMode.HTML,
#     )
# )

# # Регистрируем диалог
# dp.include_router(dialog)

# # Запуск начального окна
# @dp.message()
# async def start(message: Message, dialog_manager: DialogManager):
#     await dialog_manager.start(States.MAIN, mode=StartMode.RESET_STACK)

# # ====== Запуск бота ======
# async def main():
#     setup_dialogs(dp)
#     await dp.start_polling(bot)

# if __name__ == '__main__':
#     from aiogram_dialog.utils import setup_dialogs
#     import asyncio
#     asyncio.run(main())


from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from enum import Enum

# Состояния (States)
class MainMenuStates(Enum):
    MAIN = "main"

class SettingsStates(Enum):
    SETTINGS_MENU = "settings_menu"

# Окно главного меню
main_menu = Dialog(
    Window(
        Const("Главное меню"),
        Button(Const("Настройки"), id="settings", on_click=lambda c, b, m: m.start(SettingsStates.SETTINGS_MENU, mode=StartMode.NEW_STACK)),
        state=MainMenuStates.MAIN,
    )
)

# Окно настроек
settings_menu = Dialog(
    Window(
        Const("Меню настроек"),
        Button(Const("Назад"), id="back", on_click=lambda c, b, m: m.done()),
        state=SettingsStates.SETTINGS_MENU,
    )
)

# Обработчик /start
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuStates.MAIN, mode=StartMode.RESET_STACK)

# Инициализация
bot = Bot(token="7205076132:AAHS4bKNtfg3gD3PB7iHsszj1ZEH9rnYVtU")
dp = Dispatcher()
dp.include_router(main_menu)
dp.include_router(settings_menu)
# dp.message.middleware(SetupMiddleware())
dp.message.register(start, F.text == "/start")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))