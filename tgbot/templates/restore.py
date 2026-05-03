import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def restore_text():
    config = sett.get("config")
    
    sold = "✅" if config["playerok"]["auto_restore_items"]["sold"] else "❌"
    expired = "✅" if config["playerok"]["auto_restore_items"]["expired"] else "❌"
    all = "Все товары" if config["playerok"]["auto_restore_items"]["all"] else "Указанные товары"
    
    auto_restore_items = sett.get("auto_restore_items")
    included = len(auto_restore_items["included"])
    excluded = len(auto_restore_items["excluded"])
    
    txt = textwrap.dedent(f"""
        <b>♻️ Авто-восстановление</b>
        <blockquote><b>(?)</b> Эта функция позволит автоматически восстанавливать (заново выставлять) предмет, который только что купили или который истёк, чтобы он снова был в продаже. Предмет будет выставлен с бесплатным статусом приоритета.</blockquote>

        <b>🛒 Проданные:</b> {sold}
        <b>⏰ Истёкшие:</b> {expired}

        <b>📦 Восстанавливать:</b> {all}
        <blockquote><b>(?)</b> Если вы выберете "Все товары", то будут восстанавливаться все товары, кроме тех, что указаны в исключениях. Если вы выберете "Указанные товары", то будут восстанавливаться только те товары, которые вы добавите во включенные.</blockquote>

        <b>➕ Включенные:</b> {included}
        <b>➖ Исключенные:</b> {excluded}
    """)
    return txt


def restore_kb():
    config = sett.get("config")
    
    sold = "✅" if config["playerok"]["auto_restore_items"]["sold"] else "❌"
    expired = "✅" if config["playerok"]["auto_restore_items"]["expired"] else "❌"
    all = "Все товары" if config["playerok"]["auto_restore_items"]["all"] else "Указанные товары"
    
    auto_restore_items = sett.get("auto_restore_items")
    included = len(auto_restore_items["included"])
    excluded = len(auto_restore_items["excluded"])
    
    rows = [
        [
        InlineKeyboardButton(text=f"🛒 Проданные: {sold}", callback_data="switch_auto_restore_items_sold"),
        InlineKeyboardButton(text=f"⏰ Истёкшие: {expired}", callback_data="switch_auto_restore_items_expired")
        ],
        [InlineKeyboardButton(text=f"📦 Восстанавливать: {all}", callback_data="switch_auto_restore_items_all")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {included}", callback_data=calls.IncludedRestoreItemsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {excluded}", callback_data=calls.ExcludedRestoreItemsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def restore_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>♻️ Авто-восстановление</b>
        \n{placeholder}
    """)
    return txt