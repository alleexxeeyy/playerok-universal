import math
import textwrap
import pytz
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import Chat
from playerokapi.enums import ChatTypes, ItemDealStatuses
from utils import strip_html

from .. import callback_datas as calls


def _get_chat_info(chat: Chat):
    from plbot.playerokbot import get_playerok_bot as plbot
    
    if chat.type == ChatTypes.PM:
        user = next((u for u in chat.users if u.id != plbot().account.id), None) if chat.users else None
        username = f"👤 {user.username}"
    elif chat.type == ChatTypes.NOTIFICATIONS:
        username = "🔔 Уведомления"
    elif chat.type == ChatTypes.SUPPORT:
        username = "🛡️ Поддержка"

    unread = chat.unread_messages_counter or 0
    username = f"{username} 🔹{unread}" if unread > 0 else username
    
    msg = chat.last_message
    msg_text = ""

    if msg and msg.deal:
        if msg.deal.status == ItemDealStatuses.PAID:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Сделка оплачена*</i></a>'
        elif msg.deal.status == ItemDealStatuses.PENDING:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Товар в ожидании*</i></a>'
        elif msg.deal.status == ItemDealStatuses.SENT:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Продавец подтвердил сделку*</i></a>'
        elif msg.deal.status == ItemDealStatuses.CONFIRMED:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Покупатель подтвердил выполнение*</i></a>'
        elif msg.deal.status == ItemDealStatuses.CONFIRMED_AUTOMATICALLY:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Выполнение подтверждение автоматически*</i></a>'
        elif msg.deal.status == ItemDealStatuses.ROLLED_BACK:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Оформлен возврат*</i></a>'
        elif msg.deal.status == ItemDealStatuses.HAS_PROBLEM:
            msg_text = f'<a href="https://playerok.com/deal/{msg.deal.id}"><i>*Покупатель сообщил о проблеме*</i></a>'
    elif msg and msg.text:
        msg_text = strip_html(msg.text.replace("\n", " "))
        msg_text = msg_text[:48] + ("..." if len(msg_text) > 48 else "")
    elif not all((msg.text, msg.images)):
        msg_text = "<i>*Без сообщения*</i>"
    
    if msg.images:
        msg_text = f"<i>*Изображения ({len(msg.images)})*</i> " + msg_text

    iso_dt = msg.created_at
    if iso_dt.endswith("Z"):
        iso_dt = iso_dt[:-1] + "+00:00"

    now = datetime.now().astimezone(pytz.timezone("Europe/Moscow"))
    dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
    strf = "%H:%M:%S" if now - dt <= timedelta(days=1) else "%d.%m %H:%M:%S"
    msg_date = dt.strftime(strf)

    return username, msg_text, msg_date

                    
def chats_text(chats: list[Chat], page=0):
    items_per_page = 12
    
    total_pages = math.ceil(len(chats) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    chats_frmtd = ""
    for chat in list(chats)[start_offset:end_offset]:
        username, msg, msg_date = _get_chat_info(chat)
        chats_frmtd += (
            f"<b>{username}</b> ・ {msg_date}"
            f"\n      ┗ {msg}\n\n"
        )

    chats_frmtd = chats_frmtd.strip()
    if not chats_frmtd:
        chats_frmtd = "Не найдено чатов. Попробуйте обновить страницу"

    txt = textwrap.dedent(f"""
        <b>💬 Чаты</b>
        \n{chats_frmtd}
    """)
    return txt


def chats_kb(chats: list[Chat], page=0):
    rows = []
    items_per_page = 12
    items_per_row = 2
    
    total_pages = math.ceil(len(chats) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for chat in list(chats)[start_offset:end_offset]:
        username, _, _ = _get_chat_info(chat)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{username}", 
            callback_data=calls.ChatPage(id=chat.id).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ChatsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_chats_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ChatsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="💬 На сайте", url="https://playerok.com/chats")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ChatsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def chats_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>💬 Чаты</b>
        \n{placeholder}
    """)
    return txt