import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_auth_text():
    config = sett.get("config")
    
    cookies = config["playerok"]["api"]["cookies"][:30] + ("*" * 10) or "❌ Не задано"
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>🔑 Авторизация</b>

        <b>🍪 Cookie-данные:</b> {cookies}
        <b>🎩 User Agent:</b> {user_agent}
    """)
    return txt


def settings_auth_kb():
    config = sett.get("config")
    
    cookies = config["playerok"]["api"]["cookies"][:30] + ("*" * 10) or "❌ Не задано"
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"🍪 Cookie-данные: {cookies}", callback_data="enter_cookies")],
        [InlineKeyboardButton(text=f"🎩 User Agent: {user_agent}", callback_data="enter_user_agent")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_auth_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔑 Авторизация</b>
        \n{placeholder}
    """)
    return txt