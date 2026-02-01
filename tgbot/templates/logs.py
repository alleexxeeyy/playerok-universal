import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from settings import Settings as sett

from .. import callback_datas as calls


def logs_text():
    config = sett.get("config")
    max_file_size = config["logs"]["max_file_size"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>🗒️ Логи</b>

        <b>📄 Макс. размер файла:</b> {max_file_size} MB

        <b>Примечание:</b>
        Файл логов будет автоматически очищаться, как только его размер превысит указанный в конфиге, чтобы не занимать много места на вашем устройстве.
    """)
    return txt


def logs_kb():
    config = sett.get("config")
    max_file_size = config["logs"]["max_file_size"] or "❌ Не задано"

    rows = [
        [InlineKeyboardButton(text=f"📄 Макс. размер файла: {max_file_size} MB", callback_data="enter_logs_max_file_size")],
        [InlineKeyboardButton(text=f"📔 Получить логи", callback_data="select_logs_file_lines")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def logs_file_lines_kb():
    rows = [
        [
        InlineKeyboardButton(text=f"📗 Последние 100 строк", callback_data=calls.SendLogsFile(lines=100).pack()),
        InlineKeyboardButton(text=f"📘 Последние 250 строк", callback_data=calls.SendLogsFile(lines=250).pack())
        ],
        [
        InlineKeyboardButton(text=f"📕 Последние 1000 строк", callback_data=calls.SendLogsFile(lines=1000).pack()),
        InlineKeyboardButton(text=f"📖 Весь файл", callback_data=calls.SendLogsFile(lines=-1).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="logs").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def logs_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🗒️ Логи</b>
        \n{placeholder}
    """)
    return txt