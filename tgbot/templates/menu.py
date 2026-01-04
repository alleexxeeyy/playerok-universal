import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION

from .. import callback_datas as calls


def menu_text():
    txt = textwrap.dedent(f"""
        🏠 <b>Главное меню</b>

        <b>Playerok UNIVERSAL</b> v{VERSION}
        Бот-помощник для Playerok

        <b>Ссылки:</b>
        ・ <b>@alleexxeeyy</b> — главный и единственный разработчик
        ・ <b>@alexeyproduction</b> — канал, где публикуются новости
        ・ <b>@alexey_production_bot</b> — бот для покупки официальных модулей

        Перемещайтесь по разделам ниже ↓
    """)
    return txt


def menu_kb():
    rows = [
        [
        InlineKeyboardButton(text="⚙️", callback_data=calls.SettingsNavigation(to="default").pack()), 
        InlineKeyboardButton(text="👤", callback_data=calls.MenuNavigation(to="profile").pack()), 
        InlineKeyboardButton(text="🔌", callback_data=calls.ModulesPagination(page=0).pack()),
        InlineKeyboardButton(text="📊", callback_data=calls.MenuNavigation(to="stats").pack())
        ],
        [InlineKeyboardButton(text="📖 Инструкция", callback_data=calls.InstructionNavigation(to="default").pack())], 
        [
        InlineKeyboardButton(text="👨‍💻 Разработчик", url="https://t.me/alleexxeeyy"), 
        InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/alexeyproduction"), 
        InlineKeyboardButton(text="🤖 Наш бот", url="https://t.me/alexey_production_bot")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb