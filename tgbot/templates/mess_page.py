import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def mess_page_text(message_id: int):
    messages = sett.get("messages")
    
    enabled = "✅" if messages[message_id]["enabled"] else "❌"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>📄💬 Страница сообщения</b>
        \n<b>🆔 ID:</b> {message_id}\n<b>💡 Включено:</b> {enabled}
        \n<b>💬 Текст:</b> <blockquote>{message_text}</blockquote>
    """)
    return txt


def mess_page_kb(message_id: int, page: int = 0):
    messages = sett.get("messages")
    
    enabled = "✅" if messages[message_id]["enabled"] else "❌"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_message_enabled")],
        [InlineKeyboardButton(text=f"💬 Текст: {message_text}", callback_data="enter_message_text")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MessagesPagination(page=page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def mess_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄💬 Страница сообщения</b>
        \n{placeholder}
    """)
    return txt