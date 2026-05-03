import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls
    

def other_text():
    config = sett.get("config")
    
    read_chat = "✅" if config["playerok"]["read_chat"] else "❌"
    watermark_enabled = "✅" if config["playerok"]["watermark"]["enabled"] else "❌"
    watermark_value = config["playerok"]["watermark"]["value"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>

        <b>👀 Чтение чата:</b> {read_chat}
        <blockquote><b>(?)</b> Будет помечать чат как прочитанный перед тем, как отправить сообщение.</blockquote>

        <b>©️ Водяной знак:</b> {watermark_enabled}
        <b>🏷️©️ Значение:</b> {watermark_value}
    """)
    return txt


def other_kb():
    config = sett.get("config")
    
    read_chat = "✅" if config["playerok"]["read_chat"] else "❌"
    watermark_enabled = "✅" if config["playerok"]["watermark"]["enabled"] else "❌"
    watermark_value = config["playerok"]["watermark"]["value"] or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"👀 Чтение чата: {read_chat}", callback_data="switch_read_chat_enabled")],
        [InlineKeyboardButton(text=f"©️ Водяной знак: {watermark_enabled}", callback_data="switch_watermark_enabled")],
        [InlineKeyboardButton(text=f"🏷️©️ Значение: {watermark_value}", callback_data="enter_watermark_value")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def other_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>
        \n{placeholder}
    """)
    return txt