import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import escape_html

from .. import callback_datas as calls


def data_replacement_text(index: int):
    repl = sett.get("data_replacement")[index]

    enabled = "✅" if repl.get("enabled") else "❌"
    keyphrases = "</code>, <code>".join(escape_html(p) for p in repl.get("keyphrases", [])) or "❌ Не задано"
    separator = escape_html(repl.get("separator") or ":")
    total_data = len(repl.get("data", []))

    txt = textwrap.dedent(f"""
        <b>📄🔄 Страница замены данных</b>

        <b>⚡ Активна:</b> {enabled}
        <b>🔑 Ключевые фразы:</b> <code>{keyphrases}</code>
        <b>🔣 Разделитель:</b> <code>{separator}</code>
        <blockquote><b>(?)</b> Символ, которым разделены значения в строке данных. Значения раскладываются по полям товара в том же порядке, в котором вы заполняли их при создании товара на Playerok.</blockquote>

        <b>💽 Данные:</b> {total_data} шт.
    """)
    return txt


def data_replacement_kb(index: int, page: int = 0):
    repl = sett.get("data_replacement")[index]

    enabled = "✅" if repl.get("enabled") else "❌"
    keyphrases = ", ".join(repl.get("keyphrases", [])) or "❌ Не задано"
    separator = repl.get("separator") or ":"
    total_data = len(repl.get("data", []))

    rows = [
        [InlineKeyboardButton(text=f"⚡ Активна: {enabled}", callback_data="switch_data_replacement_enabled")],
        [InlineKeyboardButton(text=f"🔑 Ключевые фразы: {keyphrases}", callback_data="enter_data_replacement_keyphrases")],
        [InlineKeyboardButton(text=f"🔣 Разделитель: {separator}", callback_data="enter_data_replacement_separator")],
        [InlineKeyboardButton(text=f"💽 Данные: {total_data} шт. | 👈 Нажми для редактирования", callback_data=calls.DataReplacementValuesPagination(page=0).pack())],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="confirm_deleting_data_replacement")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.DataReplacementsPagination(page=page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def data_replacement_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄🔄 Страница замены данных</b>
        \n{placeholder}
    """)
    return txt
