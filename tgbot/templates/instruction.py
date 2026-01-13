import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import callback_datas as calls
                
        
def instruction_text():
    txt = textwrap.dedent(f"""
        <b>📖 Инструкция</b>
        В этом разделе описаны инструкции по работе с ботом

        Перемещайтесь по разделам ниже ↓
    """)
    return txt


def instruction_kb():
    rows = [
        [InlineKeyboardButton(text="⌨️ Команды", callback_data=calls.InstructionNavigation(to="commands").pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def instruction_comms_text():
    txt = textwrap.dedent(f"""
        <b>📖 Инструкция → ⌨️ Команды</b>
                          
        Команды покупателя:
        ・ <code>!команды</code> — отображает меню с доступными для покупателя командами
        ・ <code>!продавец</code> — уведомляет и вызывает продавца в диалог с покупателем (пишет вам в Telegram сообщение с просьбой о помощи)

        Выберите действие ↓
    """)
    return txt


def instruction_comms_kb():
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.InstructionNavigation(to="default").pack())]]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb