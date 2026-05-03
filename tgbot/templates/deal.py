import textwrap
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from playerokapi.types import ItemDeal
from playerokapi.enums import ItemDealDirections, ItemDealStatuses, MessageTemplateTypes

from .. import callback_datas as calls


def deal_text(deal: ItemDeal):
    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account

    username = deal.user.username
    username += " (Вы)" if deal.user.id == acc.id else ""

    item_name = deal.item.name
    item_image = deal.item.attachments[0].url
    item_price = deal.item.price

    status = deal.status
    if status:
        if status == ItemDealStatuses.PAID:
            status_sym = "🟢"
            status_str = "Оплачен"
        elif status == ItemDealStatuses.PENDING:
            status_sym = "🟡"
            status_str = "Ждёт отправки"
        elif status == ItemDealStatuses.SENT:
            status_sym = "🟣"
            status_str = "Продавец подтвердил"
        elif status in (ItemDealStatuses.CONFIRMED, ItemDealStatuses.CONFIRMED_AUTOMATICALLY):
            status_sym = "🔵"
            status_str = "Выполнен"
        elif status == ItemDealStatuses.ROLLED_BACK:
            status_sym = "🟠"
            status_str = "Возврат"

    data_str = ""
    if deal.item.data_fields:
        data_str = "<b>💾 Данные:</b>"
        for df in deal.item.data_fields:
            data_str += f"\n・ <b>{df.label}:</b> {df.value}"
    
    problem = ""
    if deal.has_problem and deal.status_description:
        title, text = deal.status_description.split("\n\n")
        status_desc_str = f"<b>{title}</b>\n{text}"
        problem = f"\n\n<b>🤬 Проблема:</b> <blockquote>{status_desc_str}</blockquote>"

    iso_dt = deal.created_at
    if iso_dt.endswith("Z"):
        iso_dt = iso_dt[:-1] + "+00:00"

    dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
    date = dt.strftime("%d.%m %H:%M:%S")
    
    txt = textwrap.dedent(f"""
        <b>📄📋 Страница сделки</b>
        \n<b>👤 Покупатель:</b> {username}\n<b>🏷️ Статус:</b> {status_str}
        \n<b>🛍️ Товар:</b> {item_name} <a href="{item_image}">(Изображение)</a>\n<b>💰 Цена:</b> {item_price}₽ {problem}
        \n{data_str}
        \n<b>📅 Дата создания:</b> {date}
    """)
    return txt


def deal_kb(deal: ItemDeal, last_page=0):
    rows = [
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.DealsPagination(page=last_page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.DealPage(id=deal.id).pack())
        ]
    ]
    
    if deal.direction == ItemDealDirections.OUT:
        sent_btn = InlineKeyboardButton(
            text="☑️ Подтвердить", 
            callback_data=calls.ChangeDealStatus(id=deal.id, st="SENT").pack()
        )
        rows.insert(0, [
            InlineKeyboardButton(text="🛍️ Товар", callback_data=calls.ItemPage(id=deal.item.id).pack()),
            InlineKeyboardButton(text="💬 Чат", callback_data=calls.ChatPage(id=deal.chat.id).pack())
        ])

        if deal.status != ItemDealStatuses.ROLLED_BACK:
            rows.insert(0, [InlineKeyboardButton(
                text="📦 Возврат", 
                callback_data=calls.ChangeDealStatus(id=deal.id, st="ROLLED_BACK").pack()
            )])
            if deal.status == ItemDealStatuses.PAID:
                rows[0].insert(0, sent_btn)
        elif deal.status == ItemDealStatuses.PAID:
            rows.insert(0, [sent_btn])

        rows.insert(-1, [InlineKeyboardButton(
            text="📋 Открыть на сайте", 
            url=f"https://playerok.com/deals/{deal.id}"
        )]) 
    else:
        if deal.status in (ItemDealStatuses.CONFIRMED, ItemDealStatuses.CONFIRMED_AUTOMATICALLY, ItemDealStatuses.ROLLED_BACK):
            mt_status = MessageTemplateTypes.FINISHED_DEAL_PROBLEM.value
        else:
            mt_status = MessageTemplateTypes.ACTIVE_DEAL_PROBLEM.value
            
        problem_btn = InlineKeyboardButton(
            text="🤬 Сообщить о проблеме", 
            callback_data=calls.SelMessageTemplatePagination(id=deal.id, type=mt_status, page=0).pack()
        )
        rows.insert(0, [InlineKeyboardButton(
            text="💬 Чат", 
            callback_data=calls.ChatPage(id=deal.chat.id).pack()
        )])
        rows[0].insert(0, InlineKeyboardButton(
            text="📋 Открыть на сайте", 
            url=f"https://playerok.com/deals/{deal.id}"
        )) 
        
        if deal.status == ItemDealStatuses.SENT:
            rows.insert(0, [InlineKeyboardButton(
                text="☑️ Подтвердить", 
                callback_data=calls.ChangeDealStatus(id=deal.id, st="CONFIRMED").pack()
            )])
            if not deal.has_problem:
                rows[0].insert(1, problem_btn)
        elif not deal.has_problem:
            rows.insert(0, [problem_btn])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def deal_float_text(placeholder):        
    txt = textwrap.dedent(f"""
        <b>📄📋 Страница сделки</b>
        \n{placeholder}
    """)
    return txt