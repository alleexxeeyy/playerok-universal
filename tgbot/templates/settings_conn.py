import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_conn_text():
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        <b>⚙️ Настройки → 📶 Соединение</b>

        <b>🌐 Прокси:</b> {proxy}
        <b>🛜 Таймаут подключения к playerok.com:</b> {requests_timeout}

        <b>Что такое таймаут подключения к playerok.com?</b>
        Это максимальное время, за которое должен прийти ответ на запрос с сайта Playerok. Если время истекло, а ответ не пришёл — бот выдаст ошибку. Если у вас слабый интернет, указывайте значение больше

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_conn_kb():
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"🌐 Прокси: {proxy}", callback_data="enter_proxy")],
        [InlineKeyboardButton(text=f"🛜 Таймаут подключения к playerok.com: {requests_timeout}", callback_data="enter_requests_timeout")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="conn").pack())
        ]
    ]
    if config["playerok"]["api"]["proxy"]: rows[0].append(InlineKeyboardButton(text=f"❌🌐 Убрать прокси", callback_data="clean_proxy"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_conn_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⚙️ Настройки → 📶 Соединение</b>
        \n{placeholder}
    """)
    return txt