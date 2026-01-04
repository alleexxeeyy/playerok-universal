import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_bump_included_text():
    included_bump_items = sett.get("auto_bump_items").get("included")
    txt = textwrap.dedent(f"""
        <b>⬆️ Поднятие → ➕ Включенные</b>
        Всего <b>{len(included_bump_items)}</b> включенных предметов для авто-поднятия

        Перемещайтесь по разделам ниже. Нажмите на корзину справа от ключевых фраз, чтобы удалить товар из включенных ↓
    """)
    return txt


def settings_bump_included_kb(page: int = 0):
    included_bump_items: list[list] = sett.get("auto_bump_items").get("included")
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(included_bump_items) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for keyphrases in list(included_bump_items)[start_offset:end_offset]:
        keyphrases_frmtd = ", ".join(keyphrases) or "❌ Не указано"
        rows.append([
            InlineKeyboardButton(text=f"{keyphrases_frmtd}", callback_data="123"),
            InlineKeyboardButton(text=f"🗑️", callback_data=calls.DeleteIncludedBumpItem(index=included_bump_items.index(keyphrases)).pack()),
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data="123")
        buttons_row.append(btn_back)
        
        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_messages_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_included_bump_item_keyphrases"),
        InlineKeyboardButton(text="➕📄 Добавить много", callback_data="send_new_included_bump_items_keyphrases_file"),
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="bump").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.IncludedBumpItemsPagination(page=page).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_bump_included_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⬆️ Поднятие → ➕ Включенные</b>
        \n{placeholder}
    """)
    return txt


def settings_new_bump_included_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⬆️➕ Добавление нового включенного предмета</b>
        \n{placeholder}
    """)
    return txt