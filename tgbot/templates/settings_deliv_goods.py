import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_deliv_goods_text(index=0):
    goods = sett.get("auto_deliveries")[index].get("goods", [])
    txt = textwrap.dedent(f"""
        <b>📦 Товары авто-выдачи</b>

        Всего <b>{len(goods)}</b> товаров:
    """)
    return txt


def settings_deliv_goods_kb(index=0, page=0):
    goods = sett.get("auto_deliveries")[index].get("goods", [])
    
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(goods) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for good in list(goods)[start_offset:end_offset]:
        rows.append([
            InlineKeyboardButton(text=str(good), callback_data="123"),
            InlineKeyboardButton(text="🗑️", callback_data=calls.DeleteDelivGood(index=goods.index(good)).pack()),
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.DelivGoodsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_auto_delivery_goods_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.DelivGoodsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="enter_auto_delivery_goods_add")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.AutoDeliveryPage(index=index).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_deliv_goods_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📦 Товары авто-выдачи</b>
        \n{placeholder}
    """)
    return txt


def settings_new_deliv_goods_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕📦 Добавление товара</b>
        \n{placeholder}
    """)
    return txt