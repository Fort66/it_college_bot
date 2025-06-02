from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def main_menu_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота/ вернуться в начало"),
        # BotCommand(command="traning", description="Тренажёр"),
        # BotCommand(command="exam", description="Экзамен/ Зачёт"),

    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())