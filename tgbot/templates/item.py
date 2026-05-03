import textwrap
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from playerokapi.types import MyItem, ItemPriorityStatus
from playerokapi.enums import ItemStatuses, PriorityTypes

from .. import callback_datas as calls


def item_text(item: MyItem):
    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account

    name = item.name
    desc = item.description
    image = item.attachments[0].url
    price = f"{item.raw_price}₽ <s>{item.price}</s>" if item.raw_price and item.raw_price != item.price else f"{item.price}₽"

    game = item.game.name
    cat = item.category.name
    
    priority = "Бесплатный" if item.priority == PriorityTypes.DEFAULT else "Премиум"

    status = item.status
    if status:
        if status == ItemStatuses.PENDING_APPROVAL:
            status_sym = "🟡"
            status_str = "Ожидает принятия"
        elif status == ItemStatuses.PENDING_MODERATION:
            status_sym = "🔵"
            status_str = "На модерации"
        elif status == ItemStatuses.APPROVED:
            status_sym = "🟢"
            status_str = "Активен"
        elif status == ItemStatuses.DECLINED:
            status_sym = "🔴"
            status_str = "Отклонён"
        elif status == ItemStatuses.BLOCKED:
            status_sym = "⛔"
            status_str = "Заблокирован"
        elif status == ItemStatuses.EXPIRED:
            status_sym = "🟠"
            status_str = "Истёкший"
        elif status == ItemStatuses.SOLD:
            status_sym = "⚫"
            status_str = "Продан"
        elif status == ItemStatuses.DRAFT:
            status_sym = "⚪"
            status_str = "Черновик"

    data_str = ""
    if item.data_fields:
        data_str = "<b>💾 Данные:</b>"
        for df in item.data_fields:
            data_str += f"\n・ <b>{df.label}:</b> {df.value}"

    iso_dt = item.created_at
    if iso_dt.endswith("Z"):
        iso_dt = iso_dt[:-1] + "+00:00"

    dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
    date = dt.strftime("%d.%m %H:%M:%S")
    
    txt = textwrap.dedent(f"""
        <b>📄🛍️ Страница товара</b>
        \n<b>📂 Категория:</b> {game} ({cat})\n<b>💰 Цена:</b> {price}
        \n<b>🏷️ Название:</b> {name} <a href="{image}">(Изображение)</a>\n<b>📃 Описание:</b> <blockquote>{desc}</blockquote>
        \n<b>👀 Статус:</b> {status_str}\n<b>🚀 Приоритет:</b> {priority}
        \n{data_str}
        \n<b>📅 Дата создания:</b> {date}
    """)
    return txt


def item_kb(item: MyItem, last_page=0):
    rows = [
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="confirm_delete_item")],
        [InlineKeyboardButton(text="🛍️ Открыть на сайте", url=f"https://playerok.com/products/{item.slug}")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ItemsPagination(page=last_page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ItemPage(id=item.id).pack())
        ]
    ]
    
    if item.status == ItemStatuses.DRAFT:
        rows[0].insert(0, InlineKeyboardButton(
            text="➕ Опубликовать", 
            callback_data="sel_item_pr_status"
        ))
    elif item.status == ItemStatuses.SOLD:
        rows[0].insert(0, InlineKeyboardButton(
            text="➕ Выставить повторно", 
            callback_data="sel_item_pr_status"
        ))
    elif item.status == ItemStatuses.APPROVED:
        if item.priority == PriorityTypes.DEFAULT:
            rows[0].insert(0, InlineKeyboardButton(
                text="🚀 Повысить приоритет", 
                callback_data="confirm_raise_item"
            ))
        else:
            rows[0].insert(0, InlineKeyboardButton(
                text="⬆️ Поднять", 
                callback_data="confirm_raise_item"
            ))

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def item_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>📄🛍️ Страница товара</b>
        \n{placeholder}
    """)
    return txt


def sel_item_pr_status_kb(item: MyItem, pr_statuses: list[ItemPriorityStatus]):
    free_st = next((st for st in pr_statuses if st.price == 0), None)
    prem_st = next((st for st in pr_statuses if st.price > 0), None)
    
    rows = [
        [
        InlineKeyboardButton(text=f"🟢 Бесплатный ({free_st.price}₽)", callback_data=calls.ConfirmPublishItem(st_id=free_st.id).pack()),
        InlineKeyboardButton(text=f"🚀 Премиум ({prem_st.price}₽)", callback_data=calls.ConfirmPublishItem(st_id=prem_st.id).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ItemPage(id=item.id).pack())]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb