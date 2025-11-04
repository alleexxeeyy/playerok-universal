import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import callback_datas as calls


def error_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>❌ Возникла ошибка </b>

        <blockquote>{placeholder}</blockquote>
    """)
    return txt


def back_kb(cb: str):
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=cb)]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb(confirm_cb: str, cancel_cb: str):
    rows = [[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_cb),
        InlineKeyboardButton(text="❌ Отменить", callback_data=cancel_cb)
    ]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def destroy_kb():
    rows = [[InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def do_action_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🧩 <b>Действие</b>
        \n{placeholder}
    """)
    return txt


def log_text(title: str, text: str, by: str = "playerokuniversal"):
    txt = textwrap.dedent(f"""
        <b>{title}</b>
        \n{text}
        \n<i>{by}</i>
    """)
    return txt


def log_new_mess_kb(username: str):
    rows = [[InlineKeyboardButton(text="💬 Написать", callback_data=calls.RememberUsername(name=username, do="send_mess").pack())]]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_new_deal_kb(username: str, deal_id: str):
    rows = [
        [
        InlineKeyboardButton(text="💬 Написать", callback_data=calls.RememberUsername(name=username, do="send_mess").pack()),
        InlineKeyboardButton(text="☑️ Выполнил", callback_data=calls.RememberDealId(de_id=deal_id, do="complete").pack()),
        InlineKeyboardButton(text="📦 Возврат", callback_data=calls.RememberDealId(de_id=deal_id, do="refund").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_new_review_kb(username: str, deal_id: str):
    rows = [
        [
        InlineKeyboardButton(text="💬🌟 Ответить на отзыв", callback_data=calls.RememberDealId(de_id=deal_id, do="answer_rev").pack()),
        InlineKeyboardButton(text="💬 Написать", callback_data=calls.RememberUsername(name=username, do="send_mess").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def sign_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🔐 <b>Авторизация</b>
        \n{placeholder}
    """)
    return txt


def call_seller_text(calling_name, chat_link):
    txt = textwrap.dedent(f"""
        🆘 <b>{calling_name}</b> требуется ваша помощь!
        {chat_link}
    """)
    return txt