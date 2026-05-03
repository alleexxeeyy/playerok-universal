import math
import pytz
import textwrap
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import Review
from playerokapi.enums import ReviewStatuses

from .. import callback_datas as calls


def _get_review_info(review: Review):
    username = review.creator.username
    rating = "⭐" * (review.rating or 5)
    
    text = review.text[:64] + ("..." if len(review.text) > 64 else "") if review.text else "<i>Без текста</i>"
    item_name = review.deal.item.name[:48] + ("..." if len(review.deal.item.name) > 48 else "")

    status = review.status
    if status:
        if status == ReviewStatuses.APPROVED:
            status_sym = "🟢"
            status_str = "Активен"
        elif status == ReviewStatuses.DELETED:
            status_sym = "🔴"
            status_str = "Удалён"

    iso_dt = review.created_at
    if iso_dt.endswith("Z"):
        iso_dt = iso_dt[:-1] + "+00:00"

    now = datetime.now().astimezone(pytz.timezone("Europe/Moscow"))
    dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
    strf = "%H:%M:%S" if now - dt <= timedelta(days=1) else "%d.%m %H:%M:%S"
    date = dt.strftime(strf)

    return username, rating, text, item_name, status_sym, status_str, date

                    
def reviews_text(reviews: list[Review], page=0):
    items_per_page = 12
    
    total_pages = math.ceil(len(reviews) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    reviews_frmtd = ""
    for review in list(reviews)[start_offset:end_offset]:
        username, rating, text, item_name, status_sym, status_str, date = _get_review_info(review)
        reviews_frmtd += (
            f"<b>{status_sym} {username}</b> ・ {rating} ・ {date}"
            f"\n      ┗ {text}\n\n"
        )

    from plbot.playerokbot import get_playerok_bot as plbot
    total = plbot().account.profile.reviews_count

    reviews_frmtd = reviews_frmtd.strip()
    if not reviews_frmtd:
        if total:
            reviews_frmtd = "Нету отзывов по заданным фильтрам. Попробуйте обновить страницу"
        else:
            reviews_frmtd = "У вас нету отзывов"

    txt = textwrap.dedent(f"""
        <b>🌟 Отзывы</b> ({total})
        \n{reviews_frmtd}
    """)
    return txt


def reviews_kb(reviews: list[Review], page=0):
    rows = []
    items_per_page = 12
    reviews_per_row = 1
    
    total_pages = math.ceil(len(reviews) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for review in list(reviews)[start_offset:end_offset]:
        username, rating, text, item_name, status_sym, status_str, date = _get_review_info(review)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{status_sym} {username} ・ {rating}", 
            callback_data=calls.ReviewPage(id=review.id).pack())
        )
    for i in range(0, len(dynamic_btns), reviews_per_row):
        rows.append(dynamic_btns[i:i+reviews_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ReviewsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_reviews_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ReviewsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account

    rows.append([
        InlineKeyboardButton(text="✨ Фильтр", callback_data="reviews_filter"),
        InlineKeyboardButton(text="🌟 На сайте", url=f"https://playerok.com/profile/{acc.username}/reviews")
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ReviewsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def reviews_float_text(placeholder):
    from plbot.playerokbot import get_playerok_bot as plbot

    txt = textwrap.dedent(f"""
        <b>🌟 Отзывы</b> ({plbot().account.profile.reviews_count})
        \n{placeholder}
    """)
    return txt