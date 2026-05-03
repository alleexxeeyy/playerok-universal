import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls

                    
def signed_users_text():
    config = sett.get("config")
    signed_users = config["telegram"]["bot"]["signed_users"]

    txt = textwrap.dedent(f"""
        <b>🔑 Авторизации</b>
        Всего <b>{len(signed_users)}</b> юзеров:
    """)
    return txt


async def signed_users_kb(page=0):
    config = sett.get("config")
    signed_users = config["telegram"]["bot"]["signed_users"]
    
    rows = []
    items_per_page = 7
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
            username = "@" + chat.username.replace("@", "")
        except:
            username = user_id
        rows.append([
            InlineKeyboardButton(text=username, callback_data="null_answer"),
            InlineKeyboardButton(text="🗑️", callback_data=calls.DeleteSignedUser(id=user_id).pack())
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.SignedUsersPagination(page=page - 1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.SignedUsersPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)
    
    rows.append([InlineKeyboardButton(text="🔐 Изменить ключ-пароль", callback_data="enter_current_password")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def signed_users_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>🔑 Авторизации</b>
        \n{placeholder}
    """)
    return txt