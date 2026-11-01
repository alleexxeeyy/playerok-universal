import math
import textwrap
from html import escape
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from core.blacklist import get_blacklist

from .. import callback_datas as calls


def blacklist_text():
    config = sett.get("config")
    users = get_blacklist()
    auto_refund_enabled = "✅" if config["playerok"]["blacklist"]["auto_refund"] else "❌"

    txt = textwrap.dedent(f"""
        <b>🚫 Чёрный список</b>
        Всего <b>{len(users)}</b> покупателей

        <b>📦 Авто-возврат сделок:</b> {auto_refund_enabled}

        Сделки и сообщения от покупателей из чёрного списка не передаются модулям, а уведомления о них приходят с пометкой 🚫
    """)
    return txt


def blacklist_kb(page: int = 0):
    config = sett.get("config")
    users = get_blacklist()
    auto_refund_enabled = "✅" if config["playerok"]["blacklist"]["auto_refund"] else "❌"

    rows = []
    items_per_page = 10
    total_pages = math.ceil(len(users.keys())/items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages-1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    rows.append([InlineKeyboardButton(text=f"📦 Авто-возврат сделок: {auto_refund_enabled}", callback_data="switch_blacklist_auto_refund")])

    for index, username in enumerate(list(users.keys())[start_offset:end_offset], start=start_offset):
        reason = users[username].get("reason")
        rows.append([InlineKeyboardButton(text=f"{username} — {reason}" if reason else username, callback_data=calls.BlacklistUserPage(index=index).pack())])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.BlacklistPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑",callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"📃 {page+1}/{total_pages}",callback_data=calls.PageEnter(to="blacklist", page=page, total=total_pages).pack())
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.BlacklistPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕ Добавить",callback_data="enter_new_blacklist_user")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def blacklist_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🚫 Чёрный список</b>
        \n{placeholder}
    """)
    return txt


def new_blacklist_user_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕🚫 Добавление в чёрный список</b>
        \n{placeholder}
    """)
    return txt


def new_blacklist_user_reason_kb(back_cb: str):
    rows = [
        [InlineKeyboardButton(text="➡️ Без причины", callback_data="add_new_blacklist_user")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_cb)]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def chat_blacklist_reason_kb():
    rows = [
        [InlineKeyboardButton(text="➡️ Без причины", callback_data="add_chat_to_blacklist")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def chat_blacklisted_kb():
    rows = [
        [InlineKeyboardButton(text="🗑️ Убрать из ЧС", callback_data="remove_chat_from_blacklist")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def blacklist_entry_text(entry: dict):
    reason = escape(entry.get("reason") or "") or "❌ Не указана"
    txt = textwrap.dedent(f"""
        <b>👤 Покупатель:</b> {escape(entry["username"])}
        <b>📝 Причина:</b> {reason}
    """)
    return txt
