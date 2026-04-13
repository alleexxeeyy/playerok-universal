import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_stats

from .. import callback_datas as calls


def stats_text():
    try:
        stats = get_stats()
        
        txt = textwrap.dedent(f"""
            <b>📊 Статистика</b>

            ━━━━━━━━━━━━━━
            
            <b>⏰ За последние 24 часа:</b>
            
            <b>📋 Заказы:</b>
            <b>・</b> ➕ Активных: {stats['day']['active']}
            <b>・</b> ➖ Завершённых: {stats['day']['completed']}
            <b>・</b> 🔙 Возвратов: {stats['day']['refunded']}
            <b>・</b> ♾️ Всего: {stats['day']['orders']}
            
            <b>💸 Заработано:</b> {stats['day']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['day']['best']}

            ━━━━━━━━━━━━━━

            <b>📅 За последнюю неделю:</b>
            
            <b>📋 Заказы:</b>
            <b>・</b> ➕ Активных: {stats['week']['active']}
            <b>・</b> ➖ Завершённых: {stats['week']['completed']}
            <b>・</b> 🔙 Возвратов: {stats['week']['refunded']}
            <b>・</b> ♾️ Всего: {stats['week']['orders']}
            
            <b>💸 Заработано:</b> {stats['week']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['week']['best']}

            ━━━━━━━━━━━━━━

            <b>🗓 За последний месяц:</b>
            
            <b>📋 Заказы:</b>
            <b>・</b> ➕ Активных: {stats['month']['active']}
            <b>・</b> ➖ Завершённых: {stats['month']['completed']}
            <b>・</b> 🔙 Возвратов: {stats['month']['refunded']}
            <b>・</b> ♾️ Всего: {stats['month']['orders']}
            
            <b>💸 Заработано:</b> {stats['month']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['month']['best']}

            ━━━━━━━━━━━━━━
            
            <b>📈 За все время:</b>
            
            <b>📋 Заказы:</b>
            <b>・</b> ➕ Активных: {stats['all']['active']}
            <b>・</b> ➖ Завершённых: {stats['all']['completed']}
            <b>・</b> 🔙 Возвратов: {stats['all']['refunded']}
            <b>・</b> ♾️ Всего: {stats['all']['orders']}
            
            <b>💸 Заработано:</b> {stats['all']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['all']['best']}

            ━━━━━━━━━━━━━━
            
            <i>Подсчитывается только во время использования бота</i>
        """)
        return txt
    except:
        import traceback
        traceback.print_exc()


def stats_kb():
    rows = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb