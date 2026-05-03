import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_stats

from .. import callback_datas as calls


def stats_day_text():
    stats = get_stats()
    
    txt = textwrap.dedent(f"""
        <b>📊 Статистика</b>
        
        <b>⏰ За последние 24 часа:</b>
                          
        ・ ➕ Активных: {stats['day']['active']}
        ・ ➖ Завершённых: {stats['day']['completed']}
        ・ 🔙 Возвратов: {stats['day']['refunded']}
        ・ ♾️ Всего: {stats['day']['orders']}
        
        <b>💸 Заработано:</b> {stats['day']['profit']} руб.
        <b>🔥 Лучший товар:</b> {stats['day']['best']}
        
        <i>Подсчитывается только во время использования бота</i>
    """)
    return txt


def stats_day_kb():
    rows = [
        [
        InlineKeyboardButton(text="・ ⏰ 24 часа ・", callback_data=calls.StatsNavigation(to="day").pack()),
        InlineKeyboardButton(text="📅 7 дней", callback_data=calls.StatsNavigation(to="week").pack())
        ],
        [
        InlineKeyboardButton(text="🗓 30 дней", callback_data=calls.StatsNavigation(to="month").pack()),
        InlineKeyboardButton(text="📈 Всё время", callback_data=calls.StatsNavigation(to="all").pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb