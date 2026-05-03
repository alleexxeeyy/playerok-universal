import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def complete_text():
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["auto_complete_deals"]["enabled"] else "❌"
    all = "Всех товаров" if config["playerok"]["auto_complete_deals"]["all"] else "Указанных товаров"
    
    auto_complete_deals = sett.get("auto_complete_deals")
    included = len(auto_complete_deals["included"])
    excluded = len(auto_complete_deals["excluded"])
    
    txt = textwrap.dedent(f"""
        <b>☑️ Авто-подтверждение</b>
        <blockquote><b>(?)</b> Бот будет автоматически подтверждать выполнение только что оформленных сделок.</blockquote>

        <b>💡 Включено:</b> {enabled}
        <b>📦 Подтверждать сделки:</b> {all}
        <blockquote><b>(?)</b> Если вы выберете "Всех товаров", то будут подтверждаться сделки всех товаров, кроме тех, что указаны в исключениях. Если вы выберете "Указанных товаров", то будут подтверждаться сделки только тех товаров, которые вы добавите во включенные.</blockquote>

        <b>➕ Включенные:</b> {included}
        <b>➖ Исключенные:</b> {excluded}
    """)
    return txt


def complete_kb():
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["auto_complete_deals"]["enabled"] else "❌"
    all = "Всех товаров" if config["playerok"]["auto_complete_deals"]["all"] else "Указанных товаров"
    
    auto_complete_deals = sett.get("auto_complete_deals")
    included = len(auto_complete_deals["included"])
    excluded = len(auto_complete_deals["excluded"])
    
    rows = [
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_auto_complete_deals_enabled")],
        [InlineKeyboardButton(text=f"📦 Подтверждать сделки: {all}", callback_data="switch_auto_complete_deals_all")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {included}", callback_data=calls.IncludedCompleteDealsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {excluded}", callback_data=calls.ExcludedCompleteDealsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def complete_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>☑️ Авто-подтверждение</b>
        \n{placeholder}
    """)
    return txt