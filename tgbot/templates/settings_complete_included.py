import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_complete_included_text():
    included_complete_deals = sett.get("auto_complete_deals").get("included")
    txt = textwrap.dedent(f"""
        <b>☑️➕ Включенные</b>

        Всего <b>{len(included_complete_deals)}</b> включенных предметов:
    """)
    return txt


def settings_complete_included_kb(page=0):
    included_complete_deals: list[list] = sett.get("auto_complete_deals").get("included")
    
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(included_complete_deals) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for keyphrases in list(included_complete_deals)[start_offset:end_offset]:
        keyphrases_frmtd = ", ".join(keyphrases) or "❌ Не указаны"
        rows.append([
            InlineKeyboardButton(text=f"{keyphrases_frmtd}", callback_data="123"),
            InlineKeyboardButton(text=f"🗑️", callback_data=calls.DeleteIncludedCompleteDeal(index=included_complete_deals.index(keyphrases)).pack()),
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.IncludedCompleteDealsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)
        
        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_messages_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.IncludedCompleteDealsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_included_complete_deal_keyphrases"),
        InlineKeyboardButton(text="➕📄 Добавить много", callback_data="send_new_included_complete_deals_keyphrases_file"),
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="complete").pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_complete_included_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>☑️➕ Включенные</b>
        \n{placeholder}
    """)
    return txt


def settings_new_complete_included_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>☑️➕ Добавление включенного предмета</b>
        \n{placeholder}
    """)
    return txt