import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_deliv_page_text(index: int):
    auto_deliveries = sett.get("auto_deliveries")
    deliv = auto_deliveries[index]
    
    piece = deliv.get("piece")
    piece_str = "Поштучно" if piece else "Сообщением"
    keyphrases = "</code>, <code>".join(deliv.get("keyphrases")) or "❌ Не задано"

    if piece:
        total_goods = len(deliv.get("goods", []))
        part = f"<b>📦 Товары:</b> {total_goods} шт."
    else:
        message = "\n".join(deliv.get("message")) or "❌ Не задано"
        part = f"<b>💬 Сообщение:</b> <blockquote>{message}</blockquote>"
    
    txt = textwrap.dedent(f"""
        <b>📄🚀 Страница авто-выдачи</b>

        <b>⚡ Тип выдачи:</b> {piece_str}
        <b>🔑 Ключевые фразы:</b> <code>{keyphrases}</code>
        
        {part}
    """)
    return txt


def settings_deliv_page_kb(index: int, page: int = 0):
    auto_deliveries = sett.get("auto_deliveries")
    deliv = auto_deliveries[index]
    
    piece = deliv.get("piece")
    piece_str = "Поштучно" if piece else "Сообщением"
    keyphrases = ", ".join(deliv.get("keyphrases")) or "❌ Не задано"
    
    total_goods = len(deliv.get("goods", []))
    message = "\n".join(deliv.get("message", [])) or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"⚡ Тип выдачи: {piece_str}", callback_data="switch_auto_delivery_piece")],
        [InlineKeyboardButton(text=f"🔑 Ключевые фразы: {keyphrases}", callback_data="enter_auto_delivery_keyphrases")],
        [
        InlineKeyboardButton(text=f"💬 Сообщение: {message}", callback_data="enter_auto_delivery_message")
        if not piece else InlineKeyboardButton(text=f"📦 Товары: {total_goods} шт. | 👈 Нажми для редактирования", callback_data=calls.DelivGoodsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="confirm_deleting_auto_delivery")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.AutoDeliveriesPagination(page=page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_deliv_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄🚀 Страница авто-выдачи</b>
        \n{placeholder}
    """)
    return txt


def settings_deliv_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄🚀 Страница авто-выдачи</b>
        \n{placeholder}
    """)
    return txt