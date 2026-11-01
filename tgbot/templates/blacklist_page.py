import textwrap
from html import escape
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.blacklist import get_blacklist_entry

from .. import callback_datas as calls


def blacklist_page_text(username: str):
    entry = get_blacklist_entry(username) or {"username": username}
    reason = escape(entry.get("reason") or "") or "❌ Не указана"
    try: date = datetime.fromisoformat(entry.get("date")).strftime("%d.%m.%Y %H:%M")
    except: date = "❌ Неизвестно"

    txt = textwrap.dedent(f"""
        <b>📄🚫 Покупатель в чёрном списке</b>

        <b>👤 Покупатель:</b> {escape(entry["username"])}
        <b>📝 Причина:</b> {reason}
        <b>📅 Добавлен:</b> {date}
        <b>➕ Кем:</b> {escape(entry.get("by") or "вручную")}
    """)
    return txt


def blacklist_page_kb(page: int = 0):
    rows = [
        [InlineKeyboardButton(text="🗑️ Убрать из ЧС", callback_data="confirm_removing_blacklist_user")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.BlacklistPagination(page=page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def blacklist_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄🚫 Покупатель в чёрном списке</b>
        \n{placeholder}
    """)
    return txt
