import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_bump_text():
    config = sett.get("config")
    auto_bump_items_enabled = "🟢 Включено" if config["playerok"]["auto_bump_items"]["enabled"] else "🔴 Выключено"
    auto_bump_items_all = "Все предметы" if config["playerok"]["auto_bump_items"]["all"] else "Указанные предметы"
    auto_bump_items_interval = config["playerok"]["auto_bump_items"]["interval"] or "❌ Не указано"
    auto_bump_items = sett.get("auto_bump_items")
    auto_bump_items_included = len(auto_bump_items["included"])
    auto_bump_items_excluded = len(auto_bump_items["excluded"])
    txt = textwrap.dedent(f"""
        <b>⬆️ Поднятие</b>

        <b>⬆️ Авто-поднятие предметов:</b> {auto_bump_items_enabled}
        <b>📦 Поднимать:</b> {auto_bump_items_all}
        <b>⏲️ Интервал поднятия:</b> {auto_bump_items_interval}

        <b>➕ Включенные:</b> {auto_bump_items_included}
        <b>➖ Исключенные:</b> {auto_bump_items_excluded}

        <b>Что такое авто-поднятие предметов?</b>
        Бот будет автоматически поднимать предметы, которые выйдут за указанную позицию в таблице общих товаров. То есть, будет обновлять их PREMIUM статус, чтобы они снова были в топе. Позволяет обходить конкурентов, тем самым получая больше клиентов.

        <b>Примечание:</b>
        Если вы выберете "Все предметы", то будут подниматься все товары, кроме тех, что указаны в исключениях. Если вы выберете "Указанные предметы", то будут подниматься только те товары, которые вы добавите во включенные.
    """)
    return txt


def settings_bump_kb():
    config = sett.get("config")
    auto_bump_items_enabled = "🟢 Включено" if config["playerok"]["auto_bump_items"]["enabled"] else "🔴 Выключено"
    auto_bump_items_all = "Все предметы" if config["playerok"]["auto_bump_items"]["all"] else "Указанные предметы"
    auto_bump_items_interval = config["playerok"]["auto_bump_items"]["interval"] or "❌ Не указано"
    auto_bump_items = sett.get("auto_bump_items")
    auto_bump_items_included = len(auto_bump_items["included"])
    auto_bump_items_excluded = len(auto_bump_items["excluded"])
    rows = [
        [InlineKeyboardButton(text=f"⬆️ Авто-поднятие предметов: {auto_bump_items_enabled}", callback_data="switch_auto_bump_items_enabled")],
        [InlineKeyboardButton(text=f"📦 Поднимать: {auto_bump_items_all}", callback_data="switch_auto_bump_items_all")],
        [InlineKeyboardButton(text=f"⏲️ Интервал поднятия: {auto_bump_items_interval}", callback_data="enter_auto_bump_items_interval")],
        [
        InlineKeyboardButton(text=f"➕ Включенные: {auto_bump_items_included}", callback_data=calls.IncludedBumpItemsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {auto_bump_items_excluded}", callback_data=calls.ExcludedBumpItemsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_bump_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⬆️ Поднятие</b>
        \n{placeholder}
    """)
    return txt