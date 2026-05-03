import textwrap
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from playerokapi.types import Chat, ChatMessage, UserTypes
from playerokapi.enums import ChatTypes, ItemDealStatuses

from .. import callback_datas as calls


def chat_text(chat: Chat, msgs: list[ChatMessage]):
    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account
    
    if chat.type == ChatTypes.PM:
        user = next((u for u in chat.users if u.id != acc.id), None) if chat.users else None
        chat_name = f"👤 {user.username}"
    elif chat.type == ChatTypes.NOTIFICATIONS:
        chat_name = "🔔 Уведомления"
    elif chat.type == ChatTypes.SUPPORT:
        chat_name = "🛡️ Поддержка"

    msgs_frmtd = ""
    for msg in msgs:
        if msg.user and msg.user.username:
            username = f"👤 {msg.user.username}" if msg.user.role == UserTypes.USER else msg.user.username
            if msg.user.id == acc.id:
                username = username + " (Вы)"
        else:
            username = chat_name

        msg_text = ""
        if msg.deal:
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
        elif msg.text:
            msg_text = msg.text
        elif not all((msg.text, msg.images)):
            msg_text = "<i>*Без сообщения*</i>"
        
        if msg.images:
            imgs = []
            for i, file in enumerate(msg.images, start=1):
                imgs.append(f'<a href="{file.url}">*Изображение {i}*</a>')
            msg_text = ", ".join(imgs) + ((" " + msg_text) if msg_text else "")

        iso_dt = msg.created_at
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"

        now = datetime.now().astimezone(pytz.timezone("Europe/Moscow"))
        dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
        strf = "%H:%M:%S" if now - dt <= timedelta(days=1) else "%d.%m %H:%M:%S"
        msg_date = dt.strftime(strf)

        is_read = " ・ Не прочитано" if not msg.is_read else ""

        msgs_frmtd += f"<b>{username}:</b> <i>{msg_date}{is_read}</i> <blockquote>{msg_text}</blockquote>\n\n"
    
    txt = textwrap.dedent(f"""
        <b>💬 {chat_name}</b>
        \n{msgs_frmtd}
    """)
    return txt


def chat_kb(chat: Chat, last_page=0):
    rows = [
        [
        InlineKeyboardButton(text="✏️ Ответить", callback_data="enter_chat_answer_message"),
        InlineKeyboardButton(text="⚡ Быстрый ответ", callback_data=calls.SelFastReplyPagination(id=chat.id, page=last_page).pack()),
        ],
        [InlineKeyboardButton(text="💬 Открыть на сайте", url=f"https://playerok.com/chats/{chat.id}")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ChatsPagination(page=last_page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ChatPage(id=chat.id).pack())
        ]
    ]

    unread = chat.unread_messages_counter
    if unread > 0:
        rows.insert(1, [InlineKeyboardButton(text=f"👁️ Прочитать ({unread} сообщений)", callback_data="mark_chat_as_read")])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def chat_float_text(chat: Chat, placeholder):
    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account
    
    if chat.type == ChatTypes.PM:
        user = next((u for u in chat.users if u.id != acc.id), None) if chat.users else None
        chat_name = f"👤 {user.username}"
    elif chat.type == ChatTypes.NOTIFICATIONS:
        chat_name = "🔔 Уведомления"
    elif chat.type == ChatTypes.SUPPORT:
        chat_name = "🛡️ Поддержка"
        
    txt = textwrap.dedent(f"""
        <b>💬 {chat_name}</b>
        \n{placeholder}
    """)
    return txt