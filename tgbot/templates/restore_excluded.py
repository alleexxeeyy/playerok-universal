import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import binding_title, binding_single_url

from .. import callback_datas as calls


def restore_excluded_text():
    excluded_restore_items = sett.get("auto_restore_items").get("excluded")
    txt = textwrap.dedent(f"""
        <b>♻️➖ Исключенные</b>
        Всего <b>{len(excluded_restore_items)}</b> исключенных товаров:
    """)
    return txt


def restore_excluded_kb(page=0):
    excluded_restore_items: list[list] = sett.get("auto_restore_items").get("excluded")
    
    rows = []
    items_per_page = 10
    total_pages = math.ceil(len(excluded_restore_items) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for i, entry in enumerate(list(excluded_restore_items)[start_offset:end_offset], start=start_offset):
        title = binding_title(entry, "❌ Не указаны")
        title_frmtd = title[:32] + ("..." if len(title) > 32 else "")
        url = binding_single_url(entry)
        rows.append([
            InlineKeyboardButton(text=f"{title_frmtd}", url=url)
            if url else
            InlineKeyboardButton(text=f"{title_frmtd}", callback_data="null_answer"),
            InlineKeyboardButton(text=f"🗑️", callback_data=calls.DeleteExcludedRestoreItem(index=i).pack()),
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ExcludedRestoreItemsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)
        
        btn_pages = InlineKeyboardButton(text=f"📃 {page+1}/{total_pages}", callback_data=calls.PageEnter(to="restore_excluded", page=page, total=total_pages).pack())
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ExcludedRestoreItemsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_excluded_restore_items")
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="restore").pack()),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def restore_excluded_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>♻️➖ Исключенные</b>
        \n{placeholder}
    """)
    return txt


def new_restore_excluded_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>♻️➖ Добавление исключенного товара</b>
        \n{placeholder}
    """)
    return txt