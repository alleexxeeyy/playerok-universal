import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import ItemDeal
from playerokapi.enums import ItemDealStatuses
from utils import strip_html

from .. import callback_datas as calls


def _get_deal_info(deal: ItemDeal):
    from plbot.playerokbot import get_playerok_bot as plbot
    
    username = deal.user.username
    username += " (Вы)" if deal.user.id == plbot().account.id else ""

    item_name = strip_html(deal.item.name)
    item_name = item_name[:48] + ("..." if len(item_name) > 48 else "")
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

    has_problem = " ・ <i>🤬 Проблема</i>" if deal.has_problem else ""

    return username, item_name, item_price, status_str, status_sym, has_problem

                    
def deals_text(deals: list[ItemDeal], page=0):
    items_per_page = 12
    
    total_pages = math.ceil(len(deals) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    deals_frmtd = ""
    for deal in list(deals)[start_offset:end_offset]:
        username, item_name, item_price, status_str, status_sym, has_problem = _get_deal_info(deal)
        deals_frmtd += (
            f"<b>{status_sym} {username}</b> ・ {status_str} ・ {item_price}₽{has_problem}"
            f"\n      ┗ {item_name}\n\n"
        )

    deals_frmtd = deals_frmtd.strip()
    if not deals_frmtd:
        deals_frmtd = "Нету сделок по заданным фильтрам. Попробуйте обновить страницу"

    txt = textwrap.dedent(f"""
        <b>📋 Сделки</b>
        \n{deals_frmtd}
    """)
    return txt


def deals_kb(deals: list[ItemDeal], page=0):
    rows = []
    items_per_page = 12
    items_per_row = 1
    
    total_pages = math.ceil(len(deals) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for deal in list(deals)[start_offset:end_offset]:
        username, item_name, _, _, status_sym, _ = _get_deal_info(deal)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{status_sym} {username} ・ {item_name}", 
            callback_data=calls.DealPage(id=deal.id).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.DealsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_deals_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.DealsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account

    rows.append([
        InlineKeyboardButton(text="✨ Фильтр", callback_data="deals_filter"),
        InlineKeyboardButton(text="📋 На сайте", url=f"https://playerok.com/profile/{acc.username}/sales")
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.DealsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def deals_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>📋 Сделки</b>
        \n{placeholder}
    """)
    return txt