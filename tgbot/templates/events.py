from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import textwrap
from datetime import datetime, timedelta

from data import Data as data
from settings import Settings as sett

from .. import callback_datas as calls


def events_text():
    config = sett.get("config")
    latest_events_times = data.get("latest_events_times")
    
    last_bump_items = (datetime.fromisoformat(latest_events_times["auto_bump_items"]).strftime("%d.%m.%Y %H:%M")) if latest_events_times.get("auto_bump_items") else "❌ Не было"
    next_bump_items = ((datetime.fromisoformat(latest_events_times["auto_bump_items"]) if latest_events_times.get("auto_bump_items") else datetime.now()) + timedelta(seconds=config["playerok"]["auto_bump_items"]["interval"])).strftime("%d.%m.%Y %H:%M")
    
    txt = textwrap.dedent(f"""
        <b>🚩 Ивенты</b>

        📆⬆️ <b>Поднятие предметов:</b>
        ・ <b>Последнее:</b> {last_bump_items}
        ・ <b>Следующее:</b> {next_bump_items}
    """)
    return txt


def events_kb():
    rows = [
        [InlineKeyboardButton(text="⬆️ Поднять предметы", callback_data="confirm_bump_items")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def events_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🚩 Ивенты</b>
        \n{placeholder}
    """)
    return txt