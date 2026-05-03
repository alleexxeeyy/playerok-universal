import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import callback_datas as calls


def error_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>❌ Ошибка</b>

        <blockquote>{placeholder}</blockquote>
    """)
    return txt


def new_sign_text(user):
    username = "@" + user.username.replace("@", "")
    txt = textwrap.dedent(f"""
        <b>🔑 Новая авторизация</b>

        Пользователь <b>{username}</b> только что авторизовался в боте
        
        ❗ <b>Если это были не Вы</b>, как можно скорее перейдите в раздел <b>«🔑 Авторизации»</b> в меню бота и удалите этого пользователя, а после смените пароль от Telegram бота
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
        <b>🧩 Действие</b>
        \n{placeholder}
    """)
    return txt


def log_text(title: str, text=""):
    txt = textwrap.dedent(f"""
        <b>{title}</b>
        \n{text}
    """)
    return txt


def log_new_mess_kb(chat_id: str):
    rows = [
        [
        InlineKeyboardButton(text="✏️ Ответить", callback_data=calls.RememberChatId(id=chat_id, do="send_mess").pack()),
        InlineKeyboardButton(text="⚡ Быстрый ответ", callback_data=calls.RememberChatId(id=chat_id, do="send_fast_reply").pack())
        ],
        [InlineKeyboardButton(text="💬 Диалог", callback_data=calls.ChatPage(id=chat_id).pack())],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_new_deal_kb(chat_id: str, deal_id: str):
    rows = [
        [
        InlineKeyboardButton(text="✏️ Ответить", callback_data=calls.RememberChatId(id=chat_id, do="send_mess").pack()),
        InlineKeyboardButton(text="⚡ Быстрый ответ", callback_data=calls.RememberChatId(id=chat_id, do="send_fast_reply").pack())
        ],
        [
        InlineKeyboardButton(text="☑️ Выполнил", callback_data=calls.RememberDealId(de_id=deal_id, do="complete").pack()),
        InlineKeyboardButton(text="📦 Возврат", callback_data=calls.RememberDealId(de_id=deal_id, do="refund").pack())
        ],
        [
        InlineKeyboardButton(text="💬 Диалог", callback_data=calls.ChatPage(id=chat_id).pack()),
        InlineKeyboardButton(text="📋 Сделка", callback_data=calls.DealPage(id=deal_id).pack())
        ],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_new_problem_kb(chat_id: str, deal_id: str):
    rows = [
        [
        InlineKeyboardButton(text="✏️ Ответить", callback_data=calls.RememberChatId(id=chat_id, do="send_mess").pack()),
        InlineKeyboardButton(text="⚡ Быстрый ответ", callback_data=calls.RememberChatId(id=chat_id, do="send_fast_reply").pack())
        ],
        [
        InlineKeyboardButton(text="💬 Диалог", callback_data=calls.ChatPage(id=chat_id).pack()),
        InlineKeyboardButton(text="📋 Сделка", callback_data=calls.DealPage(id=deal_id).pack())
        ],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_item_kb(item_id: str):
    rows = [
        [InlineKeyboardButton(text="🛍️ Товар", callback_data=calls.ItemPage(id=item_id).pack())],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_deal_kb(deal_id: str):
    rows = [
        [InlineKeyboardButton(text="📋 Сделка", callback_data=calls.DealPage(id=deal_id).pack())],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_transaction_kb(deal_id: str):
    rows = [
        [InlineKeyboardButton(text="💳 Транзакция", callback_data=calls.TransactionPage(id=deal_id).pack())],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def sign_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔐 Авторизация</b>
        \n{placeholder}
    """)
    return txt


def call_seller_text(username: str, chat_id: str):
    txt = textwrap.dedent(f"""
        ❗ <b>{username}</b> вызывает вас в <a href="https://playerok.com/chats/{chat_id}">чат</a>
    """)
    return txt


def call_seller_kb(chat_id: str):
    rows = [
        [InlineKeyboardButton(text="💬 Перейти в диалог", callback_data=calls.ChatPage(id=chat_id).pack())],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb