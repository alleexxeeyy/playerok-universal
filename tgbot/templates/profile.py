import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from .. import callback_datas as calls


def profile_text():
    from plbot.playerokbot import get_playerok_bot
    
    acc = get_playerok_bot().account.get()
    profile = acc.profile
    
    txt = textwrap.dedent(f"""
        <b>👤 Мой профиль</b>

        <b>🆔 ID:</b> <code>{profile.id}</code>
        <b>👤 Никнейм:</b> {profile.username}
        <b>📪 Email:</b> {profile.email}
        <b>💬 Отзывы:</b> {profile.reviews_count} (<b>Рейтинг:</b> {profile.rating} ⭐)
        
        <b>💰 Баланс:</b> {profile.balance.value if profile.balance else 0}₽
        <b>・ 👜 Доступно:</b> {profile.balance.available if profile.balance else 0}₽
        <b>・ ⌛ В процессе:</b> {profile.balance.pending_income if profile.balance else 0}₽
        <b>・ ❄️ Заморожено:</b> {profile.balance.frozen if profile.balance else 0}₽
        
        <b>📦 Предметы:</b>
        <b>・ ➕ Активные:</b> {profile.stats.items.total - profile.stats.items.finished}
        <b>・ ➖ Завершённые:</b> {profile.stats.items.finished}
        <b>・ ♾️ Всего:</b> {profile.stats.items.total}
        
        <b>🛍️ Покупки:</b>
        <b>・ ➕ Активные:</b> {profile.stats.deals.incoming.total - profile.stats.deals.incoming.finished}
        <b>・ ➖ Завершённые:</b> {profile.stats.deals.incoming.finished}
        <b>・ ♾️ Всего:</b> {profile.stats.deals.incoming.total}

        <b>🛒 Продажи:</b>
        <b>・ ➕ Активные:</b> {profile.stats.deals.outgoing.total - profile.stats.deals.outgoing.finished}
        <b>・ ➖ Завершено:</b> {profile.stats.deals.outgoing.finished}
        <b>・ ♾️ Всего:</b> {profile.stats.deals.outgoing.total}
        
        <b>📅 Дата регистрации:</b> {datetime.fromisoformat(profile.created_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M:%S')}
    """)
    return txt


def profile_kb():
    rows = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb