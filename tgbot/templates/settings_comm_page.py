import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_comm_page_text(command: str):
    custom_commands = sett.get("custom_commands")
    command_text = "\n".join(custom_commands[command]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование пользовательской команды</b>

        ⌨️ <b>Команда:</b> {command}
        💬 <b>Ответ:</b> 
        <blockquote>{command_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_comm_page_kb(command: str, page: int = 0):
    custom_commands = sett.get("custom_commands")
    command_text = "\n".join(custom_commands[command]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"✍️ Ответ: {command_text}", callback_data="enter_custom_command_answer")],
        [InlineKeyboardButton(text="🗑️ Удалить команду", callback_data="confirm_deleting_custom_command")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.CustomCommandsPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.CustomCommandPage(command=command).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_comm_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование пользовательской команды</b>
        \n{placeholder}
    """)
    return txt