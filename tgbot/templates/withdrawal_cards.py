import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import UserBankCard

from .. import callback_datas as calls


def withdrawal_cards_text(bank_cards: list[UserBankCard]):
    txt = textwrap.dedent(f"""
        <b>💳 Банковские карты</b>
        Всего <b>{len(bank_cards)}</b> карт:
    """)
    return txt


def withdrawal_cards_kb(bank_cards: list[UserBankCard], page=0):
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(bank_cards) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for card in list(bank_cards)[start_offset:end_offset]:
        card_number = f"{card.card_first_six}****{card.card_last_four}"
        rows.append([InlineKeyboardButton(
            text=f"{card_number} ({card.card_type.name})", 
            callback_data=calls.SelectBankCard(id=card.id).pack()
        )])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.BankCardsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.BankCardsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="· 💳 Карты RU ·", callback_data="123"),
        InlineKeyboardButton(text="📱 СБП банки", callback_data=calls.SbpBanksPagination(page=0).pack()),
        InlineKeyboardButton(text="💲 USDT (TRC20)", callback_data="enter_usdt_address")
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="withdrawal").pack()),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def withdrawal_cards_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>💳 Банковские карты</b>
        \n{placeholder}
    """)
    return txt