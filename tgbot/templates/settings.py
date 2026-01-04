import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_text():
    config = sett.get("config")
    token = config["playerok"]["api"]["token"][:5] + ("*" * 10) or "❌ Не задано"
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b>

        <b>Основные настройки:</b>
        ・ Токен: <b>{token}</b>
        ・ User-Agent: <b>{user_agent}</b>

        Перемещайтесь по разделам ниже, чтобы изменить значения параметров ↓
    """)
    return txt


def settings_kb():
    rows = [
        [
        InlineKeyboardButton(text="🔑 Авторизация", callback_data=calls.SettingsNavigation(to="auth").pack()),
        InlineKeyboardButton(text="📶 Соединение", callback_data=calls.SettingsNavigation(to="conn").pack()),
        ],
        [
        InlineKeyboardButton(text="✉️ Сообщения", callback_data=calls.MessagesPagination(page=0).pack()),
        InlineKeyboardButton(text="⌨️ Команды", callback_data=calls.CustomCommandsPagination(page=0).pack()),
        InlineKeyboardButton(text="🚀 Авто-выдача", callback_data=calls.AutoDeliveriesPagination(page=0).pack())
        ],
        [
        InlineKeyboardButton(text="♻️ Восстановление", callback_data=calls.SettingsNavigation(to="restore").pack()),
        InlineKeyboardButton(text="⬆️ Поднятие", callback_data=calls.SettingsNavigation(to="bump").pack()),
        ],
        [
        InlineKeyboardButton(text="👀 Логгер", callback_data=calls.SettingsNavigation(to="logger").pack()),
        InlineKeyboardButton(text="🔧 Прочее", callback_data=calls.SettingsNavigation(to="other").pack())
        ],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="default").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb