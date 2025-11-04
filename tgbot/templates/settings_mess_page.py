import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_mess_page_text(message_id: int):
    messages = sett.get("messages")
    enabled = "🟢 Включено" if messages[message_id]["enabled"] else "🔴 Выключено"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>

        🆔 <b>ID сообщения:</b> {message_id}
        💡 <b>Состояние:</b> {enabled}
        💬 <b>Текст сообщения:</b> <blockquote>{message_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_mess_page_kb(message_id: int, page: int = 0):
    messages = sett.get("messages")
    enabled = "🟢 Включено" if messages[message_id]["enabled"] else "🔴 Выключено"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"💡 Состояние: {enabled}", callback_data="switch_message_enabled")],
        [InlineKeyboardButton(text=f"💬 Текст сообщения: {message_text}", callback_data="enter_message_text")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MessagesPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MessagePage(message_id=message_id).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_mess_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>
        \n{placeholder}
    """)
    return txt