import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def data_replacement_values_text(index=0):
    values = sett.get("data_replacement")[index].get("data", [])
    txt = textwrap.dedent(f"""
        <b>💽 Данные замены</b>
        Всего <b>{len(values)}</b> строк данных:
    """)
    return txt


def data_replacement_values_kb(index=0, page=0):
    values = sett.get("data_replacement")[index].get("data", [])

    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(values) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for i in range(start_offset, min(end_offset, len(values))):
        rows.append([
            InlineKeyboardButton(text=values[i], callback_data="null_answer"),
            InlineKeyboardButton(text="🗑️", callback_data=calls.DeleteDataReplacementValue(index=i).pack()),
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.DataReplacementValuesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.DataReplacementValuesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="enter_data_replacement_values_add")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.DataReplacementPage(index=index).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def data_replacement_values_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>💽 Данные замены</b>
        \n{placeholder}
    """)
    return txt


def new_data_replacement_values_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕💽 Добавление данных</b>
        \n{placeholder}
    """)
    return txt
