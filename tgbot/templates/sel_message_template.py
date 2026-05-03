import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def fast_sel_message_template_kb(message_templates, page=0):
    rows = []
    items_per_page = 12
    
    total_pages = math.ceil(len(message_templates) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for mt in list(message_templates)[start_offset:end_offset]:
        rows.append([InlineKeyboardButton(
            text=mt.title, 
            callback_data=calls.FastSelMessageTemplate(id=mt.id).pack()
        )])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.FastSelMessageTemplatePagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)
        
        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_message_templates_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.FastSelMessageTemplatePagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def sel_message_template_kb(message_templates, deal_id, page=0):
    rows = []
    items_per_page = 12
    
    total_pages = math.ceil(len(message_templates) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for mt in list(message_templates)[start_offset:end_offset]:
        rows.append([InlineKeyboardButton(
            text=mt.title, 
            callback_data=calls.SelMessageTemplate(id=mt.id).pack()
        )])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.SelMessageTemplatePagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)
        
        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_message_templates_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.SelMessageTemplatePagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.DealPage(id=deal_id).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb