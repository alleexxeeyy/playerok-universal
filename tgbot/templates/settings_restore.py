import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_restore_text():
    config = sett.get("config")
    
    auto_restore_items_sold = "🟢 Включено" if config["playerok"]["auto_restore_items"]["sold"] else "🔴 Выключено"
    auto_restore_items_expired = "🟢 Включено" if config["playerok"]["auto_restore_items"]["expired"] else "🔴 Выключено"
    auto_restore_items_all = "Все предметы" if config["playerok"]["auto_restore_items"]["all"] else "Указанные предметы"
    auto_restore_items = sett.get("auto_restore_items")
    auto_restore_items_included = len(auto_restore_items["included"])
    auto_restore_items_excluded = len(auto_restore_items["excluded"])
    
    txt = textwrap.dedent(f"""
        <b>♻️ Авто-восстановление</b>

        <b>♻️ Авто-восстановление предметов:</b>
        <b>・ Проданные:</b> {auto_restore_items_sold}
        <b>・ Истёкшие:</b> {auto_restore_items_expired}

        <b>📦 Восстанавливать:</b> {auto_restore_items_all}

        <b>➕ Включенные:</b> {auto_restore_items_included}
        <b>➖ Исключенные:</b> {auto_restore_items_excluded}

        <b>Что за авто-восстановление предметов?</b>
        Эта функция позволит автоматически восстанавливать (заново выставлять) предмет, который только что купили или который истёк, чтобы он снова был на продаже. Предмет будет выставлен с тем же статусом приоритета, что и был раньше.

        <b>Примечание:</b>
        Если вы выберете "Все предметы", то будут восстанавливаться все товары, кроме тех, что указаны в исключениях. Если вы выберете "Указанные предметы", то будут восстанавливаться только те товары, которые вы добавите во включенные.
    """)
    return txt


def settings_restore_kb():
    config = sett.get("config")
    
    auto_restore_items_sold = "🟢 Включено" if config["playerok"]["auto_restore_items"]["sold"] else "🔴 Выключено"
    auto_restore_items_expired = "🟢 Включено" if config["playerok"]["auto_restore_items"]["expired"] else "🔴 Выключено"
    auto_restore_items_all = "Все предметы" if config["playerok"]["auto_restore_items"]["all"] else "Указанные предметы"
    auto_restore_items = sett.get("auto_restore_items")
    auto_restore_items_included = len(auto_restore_items["included"])
    auto_restore_items_excluded = len(auto_restore_items["excluded"])
    
    rows = [
        [InlineKeyboardButton(text=f"🛒 Проданные: {auto_restore_items_sold}", callback_data="switch_auto_restore_items_sold")],
        [InlineKeyboardButton(text=f"⏰ Истёкшие: {auto_restore_items_expired}", callback_data="switch_auto_restore_items_expired")],
        [InlineKeyboardButton(text=f"📦 Восстанавливать: {auto_restore_items_all}", callback_data="switch_auto_restore_items_all")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {auto_restore_items_included}", callback_data=calls.IncludedRestoreItemsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {auto_restore_items_excluded}", callback_data=calls.ExcludedRestoreItemsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_restore_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>♻️ Автор-восстановление</b>
        \n{placeholder}
    """)
    return txt