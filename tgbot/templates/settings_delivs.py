import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_delivs_text():
    auto_deliveries = sett.get("auto_deliveries")
    txt = textwrap.dedent(f"""
        <b>⚙️ Настройки → 🚀 Авто-выдача</b>
        Всего <b>{len(auto_deliveries)}</b> настроенных товаров для авто-выдачи в конфиге

        Перемещайтесь по разделам ниже. Нажмите на ID товара, чтобы перейти в редактирование его авто-выдачи ↓
    """)
    return txt


def settings_delivs_kb(page: int = 0):
    auto_deliveries: list = sett.get("auto_deliveries")
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(auto_deliveries) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for deliv in list(auto_deliveries)[start_offset:end_offset]:
        keyphrases = ", ".join(deliv.get("keyphrases")) or "❌ Не задано"
        message = "\n".join(deliv.get("message")) or "❌ Не задано"
        rows.append([InlineKeyboardButton(text=f"{keyphrases[:32] + ('...' if len(keyphrases) > 32 else '')} → {message}", callback_data=calls.AutoDeliveryPage(index=auto_deliveries.index(deliv)).pack())])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.AutoDeliveriesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_auto_deliveries_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.AutoDeliveriesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕🚀 Добавить", callback_data="enter_new_auto_delivery_keyphrases")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.AutoDeliveriesPagination(page=page).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⚙️ Настройки → ⌨️ Авто-выдача</b>
        \n{placeholder}
    """)
    return txt


def settings_new_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🚀 Добавление пользовательской авто-выдачи</b>
        \n{placeholder}
    """)
    return txt