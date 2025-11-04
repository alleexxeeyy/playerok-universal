import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_restore_text():
    config = sett.get("config")
    auto_restore_items_enabled = "🟢 Включено" if config["playerok"]["auto_restore_items"]["enabled"] else "🔴 Выключено"
    auto_restore_items_all = "Все предметы" if config["playerok"]["auto_restore_items"]["all"] else "Указанные предметы"
    auto_restore_items = sett.get("auto_restore_items")
    auto_restore_items_included = len(auto_restore_items["included"])
    auto_restore_items_excluded = len(auto_restore_items["excluded"])
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → ♻️ Восстановление</b>

        ♻️ <b>Авто-восстановление предметов:</b> {auto_restore_items_enabled}
        📦 <b>Восстанавливать:</b> {auto_restore_items_all}

        ➕ <b>Включенные:</b> {auto_restore_items_included}
        ➖ <b>Исключенные:</b> {auto_restore_items_excluded}

        <b>Что такое автоматическое восстановление предметов?</b>
        На Playerok как только ваш товар покупают - он исчезает из продажи. Эта функция позволит автоматически восстанавливать (заново выставлять) предмет, который только что купили, чтобы он снова был на продаже. Предмет будет выставлен с тем же статусом приоритета, что и был раньше.

        <b>Примечание:</b>
        Если вы выберете "Все предметы", то будут восстанавливаться все товары, кроме тех, что указаны в исключениях. Если вы выберете "Указанные предметы", то будут восстанавливаться только те товары, которые вы добавите во включенные.
        
        Выберите параметр для изменения ↓
    """)
    return txt


def settings_restore_kb():
    config = sett.get("config")
    auto_restore_items_enabled = "🟢 Включено" if config["playerok"]["auto_restore_items"]["enabled"] else "🔴 Выключено"
    auto_restore_items_all = "Все предметы" if config["playerok"]["auto_restore_items"]["all"] else "Указанные предметы"
    auto_restore_items = sett.get("auto_restore_items")
    auto_restore_items_included = len(auto_restore_items["included"])
    auto_restore_items_excluded = len(auto_restore_items["excluded"])
    rows = [
        [InlineKeyboardButton(text=f"♻️ Авто-восстановление предметов: {auto_restore_items_enabled}", callback_data="switch_auto_restore_items_enabled")],
        [InlineKeyboardButton(text=f"📦 Восстанавливать: {auto_restore_items_all}", callback_data="switch_auto_restore_items_all")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {auto_restore_items_included}", callback_data=calls.IncludedRestoreItemsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {auto_restore_items_excluded}", callback_data=calls.ExcludedRestoreItemsPagination(page=0).pack())
        ],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="items").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_restore_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → ♻️ Восстановление</b>
        \n{placeholder}
    """)
    return txt