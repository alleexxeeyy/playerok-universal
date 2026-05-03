import textwrap
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from playerokapi.types import Review
from playerokapi.enums import ReviewStatuses

from .. import callback_datas as calls


def review_text(review: Review):
    username = review.creator.username
    rating = "⭐" * (review.rating or 5)
    
    text = f"<blockquote>{review.text}</blockquote>" if review.text else "<i>Без текста</i>"
    item = review.deal.item
    
    item_name = item.name
    item_price = f"{item.raw_price}₽ <s>{item.price}</s>" if item.raw_price and item.raw_price != item.price else f"{item.price}₽"

    status = review.status
    if status:
        if status == ReviewStatuses.APPROVED:
            status_str = "Активен"
        elif status == ReviewStatuses.DELETED:
            status_str = "Удалён"

    iso_dt = review.created_at
    if iso_dt.endswith("Z"):
        iso_dt = iso_dt[:-1] + "+00:00"

    now = datetime.now().astimezone(pytz.timezone("Europe/Moscow"))
    dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
    strf = "%H:%M:%S" if now - dt <= timedelta(days=1) else "%d.%m %H:%M:%S"
    date = dt.strftime(strf)
    
    txt = textwrap.dedent(f"""
        <b>📄🌟 Страница отзыва</b>
        \n<b>👤 Оставил:</b> {username}\n<b>🔃 Статус:</b> {status_str}
        \n<b>✨ Оценка:</b> {rating}\n<b>🏷️ Текст:</b> {text}
        \n<b>🛍️ Товар:</b> {item_name}\n<b>💰 Цена:</b> {item_price}
        \n<b>📅 Дата создания:</b> {date}
    """)
    return txt


def review_kb(review: Review, last_page=0):
    rows = [
        [
        InlineKeyboardButton(text="📋 Сделка", callback_data=calls.DealPage(id=review.deal.id).pack()),
        InlineKeyboardButton(text="🛍️ Товар", callback_data=calls.ItemPage(id=review.deal.item.id).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ReviewsPagination(page=last_page).pack())]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def review_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>📄🌟 Страница отзыва</b>
        \n{placeholder}
    """)
    return txt