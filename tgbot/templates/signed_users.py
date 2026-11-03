import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls

                    
def signed_users_text():
    config = sett.get("config")
    signed_users = config["telegram"]["bot"]["signed_users"]

    return (
        "<b>🔑 Авторизации</b>"
        "\n<blockquote><b>(?)</b> Чтобы дать доступ человеку, добавьте его кнопками ниже или попросите написать боту /start — вам придёт запрос.</blockquote>"
        f"\nВсего <b>{len(signed_users)}</b> юзеров:"
    )


async def signed_users_kb(page=0):
    config = sett.get("config")
    signed_users = config["telegram"]["bot"]["signed_users"]
    
    rows = []
    items_per_page = 10
    total_pages = math.ceil(len(signed_users) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    from tgbot.telegrambot import get_telegram_bot as tgbot
    bot = tgbot().bot

    for user_id in list(signed_users)[start_offset:end_offset]:
        try:
            chat = await bot.get_chat(user_id)
            username = "@" + chat.username.replace("@", "") if chat.username else (chat.full_name or str(user_id))
        except:
            username = str(user_id) # без юзернейма или ни разу не писал боту — get_chat не отдаст
        rows.append([
            InlineKeyboardButton(text=username, callback_data="null_answer"),
            InlineKeyboardButton(text="🗑️", callback_data=calls.DeleteSignedUser(id=user_id).pack())
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.SignedUsersPagination(page=page - 1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"📃 {page+1}/{total_pages}", callback_data=calls.PageEnter(to="signed_users", page=page, total=total_pages).pack())
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.SignedUsersPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)
    
    rows.append([
        InlineKeyboardButton(text="➕ Добавить по ID", callback_data="add_signed_user_id"),
        InlineKeyboardButton(text="👤 Из контактов", callback_data="pick_signed_user")
    ])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def signed_users_float_text(placeholder):
    return f"<b>🔑 Авторизации</b>\n\n{placeholder}"