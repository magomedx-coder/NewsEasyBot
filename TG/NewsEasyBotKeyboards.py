# NewsEasyBotKeyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================
start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📰Новости📰")],[KeyboardButton(text="💡О нас💡")]], 
                                    resize_keyboard=True, 
                                    input_field_placeholder="Выберите пункт меню")

main = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="👀Смотреть все новости", callback_data="smotr")], 
                        [InlineKeyboardButton(text="🔎Сортировка", callback_data="sort")]
                        ])

sort = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="По ключевым словам", callback_data="kluch")],
                    [InlineKeyboardButton(text="По источникам", callback_data="ist")],
                    [InlineKeyboardButton(text="По ключевым словам и источникам", callback_data="oba")],
                    [InlineKeyboardButton(text="⬅️", callback_data="back")]
                    ])

# Новая клавиатура для выбора источников
sources = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Lenta.ru", callback_data="source_lenta")],
                    [InlineKeyboardButton(text="Interfax.ru", callback_data="source_interfax")],
                    [InlineKeyboardButton(text="РБК", callback_data="source_rbk")],
                    [InlineKeyboardButton(text="⬅️", callback_data="back1")]
                    ])

back1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️", callback_data="back1")]
                    ])

back2 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️", callback_data="back2")]
                    ])


def get_pagination_keyboard(page=0, total_pages=1, source=None):
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{page}_{source}"))

    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{page}_{source}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])