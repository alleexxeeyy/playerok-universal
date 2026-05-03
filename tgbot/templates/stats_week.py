import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_stats

from .. import callback_datas as calls


def stats_week_text():
    stats = get_stats()
    
    txt = textwrap.dedent(f"""
        <b>📊 Статистика</b>

        <b>📅 За последние 7 дней:</b>
                          
        ・ ➕ Активных: {stats['week']['active']}
        ・ ➖ Завершённых: {stats['week']['completed']}
        ・ 🔙 Возвратов: {stats['week']['refunded']}
        ・ ♾️ Всего: {stats['week']['orders']}
        
        <b>💸 Заработано:</b> {stats['week']['profit']} руб.
        <b>🔥 Лучший товар:</b> {stats['week']['best']}
        
        <i>Подсчитывается только во время использования бота</i>
    """)
    return txt


def stats_week_kb():
    rows = [
        [
        InlineKeyboardButton(text="⏰ 24 часа", callback_data=calls.StatsNavigation(to="day").pack()),
        InlineKeyboardButton(text="・ 📅 7 дней ・", callback_data=calls.StatsNavigation(to="week").pack())
        ],
        [
        InlineKeyboardButton(text="🗓 30 дней", callback_data=calls.StatsNavigation(to="month").pack()),
        InlineKeyboardButton(text="📈 Всё время", callback_data=calls.StatsNavigation(to="all").pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb