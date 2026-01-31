import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import SBPBankMember

from .. import callback_datas as calls


def settings_withdrawal_sbp_text(sbp_banks: list[SBPBankMember]):
    txt = textwrap.dedent(f"""
        <b>📱 СБП банки</b>

        Всего <b>{len(sbp_banks)}</b> банков:
    """)
    return txt


def settings_withdrawal_sbp_kb(sbp_banks: list[SBPBankMember], page=0):
    rows = []
    items_per_page = 30
    items_per_row = 3
    total_pages = math.ceil(len(sbp_banks) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for bank in list(sbp_banks)[start_offset:end_offset]:
        dynamic_btns.append(InlineKeyboardButton(
            text=bank.name, 
            callback_data=calls.SelectSbpBank(id=bank.id).pack()
        ))
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.SbpBanksPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_sbp_banks_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.SbpBanksPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="💳 Карты RU", callback_data=calls.BankCardsPagination(page=0).pack()),
        InlineKeyboardButton(text="· 📱 СБП банки ·", callback_data="123"),
        InlineKeyboardButton(text="💲 USDT (TRC20)", callback_data="enter_usdt_address")
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="withdrawal").pack()),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_withdrawal_sbp_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📱 СБП банки</b>
        \n{placeholder}
    """)
    return txt