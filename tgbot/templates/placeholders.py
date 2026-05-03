import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION

from .. import callback_datas as calls


def plholders_text(to):
    if to == "account":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>
            
            <b>👤 Аккаунт</b> (<code>account</code>):

            ・ <code>{account.id}</code> — ID аккаунта
            ・ <code>{account.username}</code> — Юзернейм аккаунта
            ・ <code>{account.email}</code> — Email аккаунта
            ・ <code>{account.role}</code> — Роль аккаунта
            ・ <code>{account.avatar_url}</code> — URL аватара
            ・ <code>{account.rating}</code> — Рейтинг аккаунта
            ・ <code>{account.reviews_count}</code> — Количество отзывов
            ・ <code>{account.created_at}</code> — Дата регистрации
        """)
    elif to == "user":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>
            
            <b>👤 Собеседник</b> (<code>user</code>):

            ・ <code>{user.id}</code> — ID пользователя
            ・ <code>{user.username}</code> — Юзернейм пользователя
            ・ <code>{user.role}</code> — Роль пользователя
            ・ <code>{user.avatar_url}</code> — URL аватара
            ・ <code>{user.is_online}</code> — Онлайн ли
            ・ <code>{user.is_blocked}</code> — Заблокирован ли
            ・ <code>{user.rating}</code> — Рейтинг пользователя
            ・ <code>{user.reviews_count}</code> — Количество отзывов
            ・ <code>{user.created_at}</code> — Дата регистрации
        """)
    elif to == "chat":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>
            
            <b>💬 Чат</b> (<code>chat</code>):

            ・ <code>{chat.id}</code> — ID чата
            ・ <code>{chat.type}</code> — Тип чата
            ・ <code>{chat.status}</code> — Статус чата
            ・ <code>{chat.user}</code> — Собеседник (<code>user</code>)
            ・ <code>{chat.last_message}</code> — Последнее сообщение
        """)
    elif to == "deal":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>
            
            <b>📋 Сделка</b> (<code>deal</code>):

            ・ <code>{deal.id}</code> — ID сделки
            ・ <code>{deal.status}</code> — Статус сделки
            ・ <code>{deal.user}</code> — Покупатель (<code>user</code>)
            ・ <code>{deal.item}</code> — Товар (<code>item</code>)
            ・ <code>{deal.created_at}</code> — Дата создания (покупки)
            ・ <code>{deal.completed_at}</code> — Дата выполнения
        """)
    elif to == "item":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>
            
            <b>🛍️ Товар</b> (<code>item</code>):

            ・ <code>{item.id}</code> — ID товара
            ・ <code>{item.slug}</code> — Slug товара (имя в адресной строке)
            ・ <code>{item.name}</code> — Название товара
            ・ <code>{item.description}</code> — Описание товара
            ・ <code>{item.price}</code> — Цена товара
            ・ <code>{item.raw_price}</code> — Цена без учёта скидки
            ・ <code>{item.game}</code> — Название игры товара
            ・ <code>{item.category}</code> — Название категории игры
        """)

    return txt


def plholders_kb(to, by, last_page=0):
    sym1 = "・" if to == "account" else ""
    sym2 = "・" if to == "user" else ""
    sym3 = "・" if to == "chat" else ""
    sym4 = "・" if to == "deal" else ""
    sym5 = "・" if to == "item" else ""

    if by == "mess":
        cb = calls.MessagesPagination(page=last_page).pack()
    else:
        cb = calls.CustomCommandsPagination(page=last_page).pack()

    if by == "mess":
        rows = [
            [
            InlineKeyboardButton(text=f"{sym1} 👤 Аккаунт {sym1}", callback_data=calls.PlaceholdersNavigation(to="account", by=by).pack()),
            InlineKeyboardButton(text=f"{sym2} 👤 Собеседник {sym2}", callback_data=calls.PlaceholdersNavigation(to="user", by=by).pack())
            ],
            [
            InlineKeyboardButton(text=f"{sym3} 💬 Чат {sym3}", callback_data=calls.PlaceholdersNavigation(to="chat", by=by).pack()),
            InlineKeyboardButton(text=f"{sym4} 📋 Сделка {sym4}", callback_data=calls.PlaceholdersNavigation(to="deal", by=by).pack())
            ],
            [InlineKeyboardButton(text=f"{sym5} 🛍️ Товар {sym5}", callback_data=calls.PlaceholdersNavigation(to="item", by=by).pack())],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=cb)],
        ]
    else:
        rows = [
            [
            InlineKeyboardButton(text=f"{sym1} 👤 Аккаунт {sym1}", callback_data=calls.PlaceholdersNavigation(to="account", by=by).pack()),
            InlineKeyboardButton(text=f"{sym2} 👤 Собеседник {sym2}", callback_data=calls.PlaceholdersNavigation(to="user", by=by).pack())
            ],
            [InlineKeyboardButton(text=f"{sym3} 💬 Чат {sym3}", callback_data=calls.PlaceholdersNavigation(to="chat", by=by).pack())],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=cb)],
        ]

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb