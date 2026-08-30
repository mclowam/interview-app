from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

POSITIONS = {
    "backend": "Бэкенд",
    "frontend": "Фронтенд",
    "data_engineer": "Дата-инженер",
    "devops": "DevOps",
    "ml_engineer": "Машинное обучение",
    "fullstack": "Фуллстек"

}
LEVELS = {
    "junior": (1, "Джуниор"),
    "middle": (2, "Мидл"),
    "senior": (3, "Сеньор"),
}


def positions_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in POSITIONS.items():
        builder.button(text=label, callback_data=f"position:{key}")
    builder.adjust(2)
    return builder.as_markup()


def levels_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, (_value, label) in LEVELS.items():
        builder.button(text=label, callback_data=f"level:{key}")
    builder.adjust(3)
    return builder.as_markup()


def continue_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Следующий вопрос", callback_data="continue")
    builder.button(text="Закончить", callback_data="finish")
    builder.adjust(2)
    return builder.as_markup()
