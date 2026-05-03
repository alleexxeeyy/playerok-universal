import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def fast_replies_text():
    fast_replies = sett.get("fast_replies")
    txt = textwrap.dedent(f"""
        <b>⚡ Быстрые ответы</b>
        Всего <b>{len(fast_replies)}</b> шаблонов:
    """)
    return txt


def fast_replies_kb(page=0):
    fast_replies = sett.get("fast_replies")
    
    rows = []
    items_per_page = 8
    total_pages = math.ceil(len(fast_replies) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for reply in list(fast_replies)[start_offset:end_offset]:
        rows.append([
            InlineKeyboardButton(text=reply, callback_data=calls.EnterFastReplyText(index=fast_replies.index(reply)).pack()),
            InlineKeyboardButton(text=f"🗑️", callback_data=calls.DeleteFastReply(index=fast_replies.index(reply)).pack())
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.FastRepliesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)
        
        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_fast_replies_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.FastRepliesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_fast_reply_text")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def fast_replies_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⚡ Быстрые ответы</b>
        \n{placeholder}
    """)
    return txt


def new_fast_reply_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕⚡ Добавлениe быстрого ответа</b>
        \n{placeholder}
    """)
    return txt