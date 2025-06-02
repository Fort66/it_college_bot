from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup

from functions.load_json_file import load_file

from icecream import ic

class Keyboards:
    def __init__(self, json_file=None, data=None):
        self.reply_kb = ReplyKeyboardBuilder()
        self.inline_kb = InlineKeyboardBuilder()
        self.data = data
        self.json_file = json_file
        self.__post_init__()

    def __post_init__(self):
        if self.json_file:
            self.json_data = load_file(self.json_file, True)
        elif self.data:
            self.json_data = self.data

    async def inline_kb_generator(self, ajust_value=1):
        for value in self.json_data.keys():
            self.inline_kb.button(text=self.json_data[value]['text'], callback_data=self.json_data[value]['callback_data'])
        return self.inline_kb.adjust(ajust_value).as_markup()

    def reply_kb_generator(self, adjust_value=1):
        for value in self.json_data.keys():
            self.reply_kb.button(text=self.json_data[value]['text'])
        return self.reply_kb.adjust(adjust_value).as_markup(resize_keyboard=True)

