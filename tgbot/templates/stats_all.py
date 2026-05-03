import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_stats

from .. import callback_datas as calls


def stats_all_text():
    stats = get_stats()
    
    txt = textwrap.dedent(f"""
        <b>📊 Статистика</b>
                          
        <b>📈 За всё время:</b>
        
        ・ ➕ Активных: {stats['all']['active']}
        ・ ➖ Завершённых: {stats['all']['completed']}
        ・ 🔙 Возвратов: {stats['all']['refunded']}
        ・ ♾️ Всего: {stats['all']['orders']}
        
        <b>💸 Заработано:</b> {stats['all']['profit']} руб.
        <b>🔥 Лучший товар:</b> {stats['all']['best']}
        
        <i>Подсчитывается только во время использования бота</i>
    """)
    return txt


def stats_all_kb():
    rows = [
        [
        InlineKeyboardButton(text="⏰ 24 часа", callback_data=calls.StatsNavigation(to="day").pack()),
        InlineKeyboardButton(text="📅 7 дней", callback_data=calls.StatsNavigation(to="week").pack())
        ],
        [
        InlineKeyboardButton(text="🗓 30 дней", callback_data=calls.StatsNavigation(to="month").pack()),
        InlineKeyboardButton(text="・ 📈 Всё время ・", callback_data=calls.StatsNavigation(to="all").pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb