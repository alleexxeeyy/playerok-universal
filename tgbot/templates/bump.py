import textwrap
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import get_event_next_time

from .. import callback_datas as calls


def bump_text():
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["auto_bump_items"]["enabled"] else "❌"
    all = "Все товары" if config["playerok"]["auto_bump_items"]["all"] else "Указанные товары"
    interval = config["playerok"]["auto_bump_items"]["interval"] or "❌ Не указано"
    
    auto_bump_items = sett.get("auto_bump_items")
    included = len(auto_bump_items["included"])
    excluded = len(auto_bump_items["excluded"])

    last_time_iso = config["playerok"]["auto_bump_items"]["last_time"]
    last_time = datetime.fromisoformat(last_time_iso).strftime("%d.%m.%Y %H:%M:%S") if last_time_iso else "никогда"

    if config["playerok"]["auto_bump_items"]["enabled"]:
        if not last_time_iso:
            next_time = "прямо сейчас"
        else:
            next_time = get_event_next_time(last_time_iso, config["playerok"]["auto_bump_items"]["interval"]).strftime("%d.%m.%Y %H:%M:%S")
    else:
        next_time = "никогда"
    
    txt = textwrap.dedent(f"""
        <b>⬆️ Авто-поднятие</b>
        <blockquote><b>(?)</b> Бот будет автоматически поднимать товары по интервалу, то есть, будет обновлять их PREMIUM статус, чтобы они снова были в топе.</blockquote>

        <b>💡 Включено:</b> {enabled}
        <b>⏰ Интервал:</b> {interval} сек.

        <b>📦 Поднимать:</b> {all}
        <blockquote><b>(?)</b> Если вы выберете "Все товары", то будут подниматься все товары, кроме тех, что указаны в исключениях. Если вы выберете "Указанные товары", то будут подниматься только те товары, которые вы добавите во включенные.</blockquote>

        <b>➕ Включенные:</b> {included}
        <b>➖ Исключенные:</b> {excluded}

        ⏮️ Последний раз было <b>{last_time}</b>
        ⏭️ Следующий раз будет <b>{next_time}</b>
    """)
    return txt


def bump_kb():
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["auto_bump_items"]["enabled"] else "❌"
    all = "Все товары" if config["playerok"]["auto_bump_items"]["all"] else "Указанные товары"
    interval = config["playerok"]["auto_bump_items"]["interval"] or "❌ Не указано"
    
    auto_bump_items = sett.get("auto_bump_items")
    included = len(auto_bump_items["included"])
    excluded = len(auto_bump_items["excluded"])
    
    rows = [
        [InlineKeyboardButton(text=f"⬆️ Поднять товары", callback_data="confirm_bump_items")],
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_auto_bump_items_enabled")],
        [InlineKeyboardButton(text=f"📦 Поднимать: {all}", callback_data="switch_auto_bump_items_all")],
        [InlineKeyboardButton(text=f"⏰ Интервал: {interval} сек.", callback_data="enter_auto_bump_items_interval")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {included}", callback_data=calls.IncludedBumpItemsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {excluded}", callback_data=calls.ExcludedBumpItemsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def bump_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⬆️ Авто-поднятие</b>
        \n{placeholder}
    """)
    return txt