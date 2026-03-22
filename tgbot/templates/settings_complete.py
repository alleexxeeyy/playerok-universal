import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_complete_text():
    config = sett.get("config")
    
    enabled = "🟢 Включено" if config["playerok"]["auto_complete_deals"]["enabled"] else "🔴 Выключено"
    all = "Всех предметов" if config["playerok"]["auto_complete_deals"]["all"] else "Указанных предметов"
    
    auto_complete_deals = sett.get("auto_complete_deals")
    included = len(auto_complete_deals["included"])
    excluded = len(auto_complete_deals["excluded"])
    
    txt = textwrap.dedent(f"""
        <b>☑️ Авто-подтверждение</b>

        <b>☑️ Авто-подтверждение сделок:</b> {enabled}
        <b>📦 Подтверждать сделки:</b> {all}

        <b>➕ Включенные:</b> {included}
        <b>➖ Исключенные:</b> {excluded}

        <b>Что за авто-подтверждение сделок?</b>
        Бот будет автоматически подтверждать выполнение только что оформленных сделок.

        <b>Примечание:</b>
        Если вы выберете "Всех предметов", то будут подтверждаться сделки всех предметов, кроме тех, что указаны в исключениях. Если вы выберете "Указанных предметов", то будут подтверждаться сделки только тех товаров, которые вы добавите во включенные.
    """)
    return txt


def settings_complete_kb():
    config = sett.get("config")
    
    enabled = "🟢 Включено" if config["playerok"]["auto_complete_deals"]["enabled"] else "🔴 Выключено"
    all = "Всех предметов" if config["playerok"]["auto_complete_deals"]["all"] else "Указанных предметов"
    
    auto_complete_deals = sett.get("auto_complete_deals")
    included = len(auto_complete_deals["included"])
    excluded = len(auto_complete_deals["excluded"])
    
    rows = [
        [InlineKeyboardButton(text=f"☑️ Авто-подтверждение сделок: {enabled}", callback_data="switch_auto_complete_deals_enabled")],
        [InlineKeyboardButton(text=f"📦 Подтверждать сделки: {all}", callback_data="switch_auto_complete_deals_all")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {included}", callback_data=calls.IncludedCompleteDealsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {excluded}", callback_data=calls.ExcludedCompleteDealsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_complete_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>☑️ Авто-подтверждение</b>
        \n{placeholder}
    """)
    return txt