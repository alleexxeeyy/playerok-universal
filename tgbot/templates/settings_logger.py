import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_logger_text():
    config = sett.get("config")
    tg_logging_enabled = "🟢 Включено" if config["playerok"]["tg_logging"]["enabled"] else "🔴 Выключено"
    tg_logging_chat_id = config["playerok"]["tg_logging"]["chat_id"] or "✔️ Ваш чат с ботом"
    tg_logging_events = config["playerok"]["tg_logging"]["events"] or {}
    event_new_user_message = "🟢" if tg_logging_events["new_user_message"] else "🔴"
    event_new_system_message = "🟢" if tg_logging_events["new_system_message"] else "🔴"
    event_new_deal = "🟢" if tg_logging_events["new_deal"] else "🔴"
    event_new_review = "🟢" if tg_logging_events["new_review"] else "🔴"
    event_new_problem = "🟢" if tg_logging_events["new_problem"] else "🔴"
    event_deal_status_changed = "🟢" if tg_logging_events["deal_status_changed"] else "🔴"
    txt = textwrap.dedent(f"""
        <b>⚙️ Настройки → 👀 Логгер</b>

        <b>👀 Логгирование ивентов Playerok в Telegram:</b> {tg_logging_enabled}
        <b>💬 ID чата для логов:</b> {tg_logging_chat_id}
        <b>📢 Ивенты логгирования:</b>
        ・ {event_new_user_message} <b>💬👤 Новое сообщение от пользователя</b>
        ・ {event_new_system_message} <b>💬⚙️ Новое системное сообщение</b>
        ・ {event_new_deal} <b>📋 Новая сделка</b>
        ・ {event_new_review} <b>💬✨ Новый отзыв</b>
        ・ {event_new_problem} <b>🤬 Новая жалоба в сделке</b>
        ・ {event_deal_status_changed} <b>🔄️📋 Статус сделки изменился</b>
        
        Выберите параметр для изменения ↓
    """)
    return txt


def settings_logger_kb():
    config = sett.get("config")
    tg_logging_enabled = "🟢 Включено" if config["playerok"]["tg_logging"]["enabled"] else "🔴 Выключено"
    tg_logging_chat_id = config["playerok"]["tg_logging"]["chat_id"] or "✔️ Ваш чат с ботом"
    tg_logging_events = config["playerok"]["tg_logging"]["events"] or {}
    event_new_user_message = "🟢" if tg_logging_events["new_user_message"] else "🔴"
    event_new_system_message = "🟢" if tg_logging_events["new_system_message"] else "🔴"
    event_new_deal = "🟢" if tg_logging_events["new_deal"] else "🔴"
    event_new_review = "🟢" if tg_logging_events["new_review"] else "🔴"
    event_new_problem = "🟢" if tg_logging_events["new_problem"] else "🔴"
    event_deal_status_changed = "🟢" if tg_logging_events["deal_status_changed"] else "🔴"
    rows = [
        [InlineKeyboardButton(text=f"👀 Логгирование ивентов Playerok в Telegram: {tg_logging_enabled}", callback_data="switch_tg_logging_enabled")],
        [InlineKeyboardButton(text=f"💬 ID чата для логов: {tg_logging_chat_id}", callback_data="enter_tg_logging_chat_id")],
        [
        InlineKeyboardButton(text=f"{event_new_user_message} 💬👤 Новое сообщение от пользователя", callback_data="switch_tg_logging_event_new_user_message"),
        InlineKeyboardButton(text=f"{event_new_system_message} 💬⚙️ Новое системное сообщение", callback_data="switch_tg_logging_event_new_system_message"),
        InlineKeyboardButton(text=f"{event_new_deal} 📋 Новая сделка", callback_data="switch_tg_logging_event_new_deal")
        ],
        [
        InlineKeyboardButton(text=f"{event_new_review} 💬✨ Новый отзыв", callback_data="switch_tg_logging_event_new_review"),
        InlineKeyboardButton(text=f"{event_new_problem} 🤬 Новая жалоба в сделке", callback_data="switch_tg_logging_event_new_problem"),
        InlineKeyboardButton(text=f"{event_deal_status_changed} 🔄️📋 Статус сделки изменился", callback_data="switch_tg_logging_event_deal_status_changed")
        ],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="logger").pack())
        ]
    ]
    if config["playerok"]["tg_logging"]["chat_id"]:
        rows[1].append(InlineKeyboardButton(text=f"❌💬 Очистить", callback_data="clean_tg_logging_chat_id"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_logger_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⚙️ Настройки → 👀 Логгер</b>
        \n{placeholder}
    """)
    return txt