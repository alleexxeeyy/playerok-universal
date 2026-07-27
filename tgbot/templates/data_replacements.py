import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def data_replacements_text():
    data_replacement = sett.get("data_replacement")
    txt = textwrap.dedent(f"""
        <b>🔄 Замена данных</b>
        Всего <b>{len(data_replacement)}</b> замен данных:
    """)
    return txt


def data_replacements_kb(page=0):
    data_replacement: list = sett.get("data_replacement")

    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(data_replacement) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for i, repl in enumerate(data_replacement[start_offset:end_offset], start=start_offset):
        sym = "✅" if repl.get("enabled") else "❌"
        keyphrases = ", ".join(repl.get("keyphrases", [])) or "❌ Не задано"
        keyphrases_frmtd = keyphrases[:32] + ("..." if len(keyphrases) > 32 else "")
        total_data = len(repl.get("data", []))

        rows.append([InlineKeyboardButton(
            text=f"{sym} {keyphrases_frmtd} ・ {total_data} данных",
            callback_data=calls.DataReplacementPage(index=i).pack()
        )])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.DataReplacementsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_data_replacements_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.DataReplacementsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_data_replacement_keyphrases")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="restore").pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def data_replacements_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔄 Замена данных</b>
        \n{placeholder}
    """)
    return txt


def new_data_replacement_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕🔄 Добавление замены данных</b>
        \n{placeholder}
    """)
    return txt
