import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls
    

def updates_text():
    config = sett.get("config")
    
    auto_update = "✅" if config["updates"]["auto_update"] else "❌"
    notify = "✅" if config["updates"]["notify"] else "❌"
    
    txt = textwrap.dedent(f"""
        <b>🔃 Обновления</b>

        <b>⬇️ Авто-установка:</b> {auto_update}
        <blockquote><b>(?)</b> Бот будет автоматически обновляться до последней версии при запуске (не во время работы).</blockquote>

        <b>🔔 Оповещать:</b> {notify}
        <blockquote><b>(?)</b> При выходе новой версии вам будет приходить оповещение в этом Telegram боте.</blockquote>
    """)
    return txt


def updates_kb():
    config = sett.get("config")
    
    auto_update = "✅" if config["updates"]["auto_update"] else "❌"
    notify = "✅" if config["updates"]["notify"] else "❌"
    
    rows = [
        [InlineKeyboardButton(text=f"⬇️ Авто-установка: {auto_update}", callback_data="switch_updates_auto_update")],
        [InlineKeyboardButton(text=f"🔔 Оповещать: {notify}", callback_data="switch_updates_notify")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def updates_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔃 Обновления</b>
        \n{placeholder}
    """)
    return txt