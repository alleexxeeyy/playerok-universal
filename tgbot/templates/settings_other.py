import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls
    

def settings_other_text():
    config = sett.get("config")
    switch_read_chat_enabled = "🟢 Включено" if config["playerok"]["read_chat"]["enabled"] else "🔴 Выключено"
    auto_complete_deals_enabled = "🟢 Включено" if config["playerok"]["auto_complete_deals"]["enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["playerok"]["custom_commands"]["enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["playerok"]["auto_deliveries"]["enabled"] else "🔴 Выключено"
    watermark_enabled = "🟢 Включено" if config["playerok"]["watermark"]["enabled"] else "🔴 Выключено"
    watermark_value = config["playerok"]["watermark"]["value"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>

        <b>👀 Чтение чата перед отправкой сообщения:</b> {switch_read_chat_enabled}
        <b>☑️ Авто-подтверждение заказов:</b> {auto_complete_deals_enabled}
        <b>⌨️ Пользовательские команды:</b> {custom_commands_enabled}
        <b>🚀 Авто-выдача:</b> {auto_deliveries_enabled}
        
        <b>©️ Водяной знак под сообщениями:</b> {watermark_enabled}
        <b>✍️©️ Водяной знак:</b> {watermark_value}
    """)
    return txt


def settings_other_kb():
    config = sett.get("config")
    switch_read_chat_enabled = "🟢 Включено" if config["playerok"]["read_chat"]["enabled"] else "🔴 Выключено"
    auto_complete_deals_enabled = "🟢 Включено" if config["playerok"]["auto_complete_deals"]["enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["playerok"]["custom_commands"]["enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["playerok"]["auto_deliveries"]["enabled"] else "🔴 Выключено"
    watermark_enabled = "🟢 Включено" if config["playerok"]["watermark"]["enabled"] else "🔴 Выключено"
    watermark_value = config["playerok"]["watermark"]["value"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"👀 Чтение чата перед отправкой сообщения: {switch_read_chat_enabled}", callback_data="switch_read_chat_enabled")],
        [InlineKeyboardButton(text=f"☑️ Авто-подтверждение заказов: {auto_complete_deals_enabled}", callback_data="switch_auto_complete_deals_enabled")],
        [InlineKeyboardButton(text=f"⌨️ Пользовательские команды: {custom_commands_enabled}", callback_data="switch_custom_commands_enabled")],
        [InlineKeyboardButton(text=f"🚀 Авто-выдача: {auto_deliveries_enabled}", callback_data="switch_auto_deliveries_enabled")],
        [InlineKeyboardButton(text=f"©️ Водяной знак под сообщениями: {watermark_enabled}", callback_data="switch_watermark_enabled")],
        [InlineKeyboardButton(text=f"✍️©️ Водяной знак: {watermark_value}", callback_data="enter_watermark_value")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_other_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>
        \n{placeholder}
    """)
    return txt