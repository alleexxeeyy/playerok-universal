import textwrap
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import get_bump_next_time, is_bump_night_now

from .. import callback_datas as calls


def bump_text():
    config = sett.get("config")
    bump = config["playerok"]["auto_bump_items"]
    night = bump["night"]

    enabled = "✅" if bump["enabled"] else "❌"
    mode = "По позиции" if bump["mode"] == "position" else "По интервалу"
    all = "Все товары" if bump["all"] else "Указанные товары"
    interval = bump["interval"] or "❌ Не указано"
    position = bump["position"] or "❌ Не указано"
    cooldown = bump["cooldown"] or "❌ Не указано"
    check_interval = bump["check_interval"] or 120
    night_enabled = "✅" if night["enabled"] else "❌"
    night_interval = night["interval"] or "❌ Не указано"
    night_position = night["position"] or "❌ Не указано"

    auto_bump_items = sett.get("auto_bump_items")
    included = len(auto_bump_items["included"])
    excluded = len(auto_bump_items["excluded"])

    now_dt = datetime.now()
    now = "🌙 Ночь" if is_bump_night_now(config, now_dt) else "☀️ День"

    if bump["mode"] == "position":
        about = (
            "<blockquote><b>(?)</b> Бот будет проверять позицию товаров в их категории, "
            "и как только товар выпадет за указанную позицию — поднимет его, то есть, обновит его PREMIUM статус, "
            "чтобы он снова был в топе.</blockquote>"
        )
        if night["enabled"]:
            params = textwrap.dedent(f"""
                <b>📊☀️ Позиция днём:</b> {position}
                <b>📊🌙 Позиция ночью:</b> {night_position}
                <b>🕓 Время ночи:</b> с {night['time_from']} по {night['time_to']}
                <blockquote><b>(?)</b> В указанный промежуток товары поднимаются по ночной позиции, в остальное время — по дневной. Промежуток может переходить через полночь, например, с 23:00 по 08:00.</blockquote>

                📍 Сейчас по вашим настройкам: <b>{now}</b>
            """)
        else:
            params = textwrap.dedent(f"""
                <b>📊 Позиция:</b> {position}
            """).lstrip("\n")
        params += textwrap.dedent(f"""
            <b>🕒 Кулдаун:</b> {cooldown} сек.
            <blockquote><b>(?)</b> Минимальное время между поднятиями одного и того же товара. Защищает от слива баланса, если товар постоянно выпадает из топа. Проверка позиций происходит раз в {check_interval} сек., и товар поднимается только если он вне позиции 2 проверки подряд.</blockquote>
        """)
        footer_iso = bump["last_check_time"]
        footer_last_name = "Последняя проверка была"
        footer_next_name = "Следующая проверка будет"
        next_time_dt = (
            datetime.fromisoformat(footer_iso) + timedelta(seconds=check_interval)
            if footer_iso else now_dt
        ) if bump["enabled"] else None
    else:
        about = (
            "<blockquote><b>(?)</b> Бот будет автоматически поднимать товары по интервалу, то есть, "
            "будет обновлять их PREMIUM статус, чтобы они снова были в топе.</blockquote>"
        )
        if night["enabled"]:
            params = textwrap.dedent(f"""
                <b>⏰☀️ Интервал днём:</b> {interval} сек.
                <b>⏰🌙 Интервал ночью:</b> {night_interval} сек.
                <b>🕓 Время ночи:</b> с {night['time_from']} по {night['time_to']}
                <blockquote><b>(?)</b> В указанный промежуток товары поднимаются по ночному интервалу, в остальное время — по дневному. Промежуток может переходить через полночь, например, с 23:00 по 08:00.</blockquote>

                📍 Сейчас по вашим настройкам: <b>{now}</b>
            """)
        else:
            params = textwrap.dedent(f"""
                <b>⏰ Интервал:</b> {interval} сек.
            """).lstrip("\n")
        footer_iso = bump["last_time"]
        footer_last_name = "Последний раз было"
        footer_next_name = "Следующий раз будет"
        next_time_dt = get_bump_next_time(config, footer_iso, now_dt) if bump["enabled"] else None

    last_time = datetime.fromisoformat(footer_iso).strftime("%d.%m.%Y %H:%M:%S") if footer_iso else "никогда"
    if not next_time_dt:
        next_time = "никогда"
    elif next_time_dt <= now_dt:
        next_time = "прямо сейчас"
    else:
        next_time = next_time_dt.strftime("%d.%m.%Y %H:%M:%S")

    txt = textwrap.dedent(f"""
        <b>⬆️ Авто-поднятие</b>
        {about}

        <b>💡 Включено:</b> {enabled}
        <b>🔀 Способ:</b> {mode}
        <b>🌙 Ночной режим:</b> {night_enabled}
    """) + params + textwrap.dedent(f"""
        <b>📦 Поднимать:</b> {all}
        <blockquote><b>(?)</b> Если вы выберете "Все товары", то будут подниматься все товары, кроме тех, что указаны в исключениях. Если вы выберете "Указанные товары", то будут подниматься только те товары, которые вы добавите во включенные.</blockquote>

        <b>➕ Включенные:</b> {included}
        <b>➖ Исключенные:</b> {excluded}

        ⏮️ {footer_last_name} <b>{last_time}</b>
        ⏭️ {footer_next_name} <b>{next_time}</b>
    """)
    return txt


def bump_kb():
    config = sett.get("config")
    bump = config["playerok"]["auto_bump_items"]
    night = bump["night"]

    enabled = "✅" if bump["enabled"] else "❌"
    mode = "По позиции" if bump["mode"] == "position" else "По интервалу"
    all = "Все товары" if bump["all"] else "Указанные товары"
    interval = bump["interval"] or "❌ Не указано"
    position = bump["position"] or "❌ Не указано"
    cooldown = bump["cooldown"] or "❌ Не указано"
    night_enabled = "✅" if night["enabled"] else "❌"
    night_interval = night["interval"] or "❌ Не указано"
    night_position = night["position"] or "❌ Не указано"

    auto_bump_items = sett.get("auto_bump_items")
    included = len(auto_bump_items["included"])
    excluded = len(auto_bump_items["excluded"])

    if bump["mode"] == "position":
        if night["enabled"]:
            param_rows = [
                [
                InlineKeyboardButton(text=f"📊☀️ Днём: {position}", callback_data="enter_auto_bump_items_position"),
                InlineKeyboardButton(text=f"📊🌙 Ночью: {night_position}", callback_data="enter_auto_bump_items_night_position")
                ],
                [
                InlineKeyboardButton(text=f"🕓 Ночь с: {night['time_from']}", callback_data="enter_auto_bump_items_night_time_from"),
                InlineKeyboardButton(text=f"🕗 Ночь по: {night['time_to']}", callback_data="enter_auto_bump_items_night_time_to")
                ]
            ]
        else:
            param_rows = [
                [InlineKeyboardButton(text=f"📊 Позиция: {position}", callback_data="enter_auto_bump_items_position")]
            ]
        param_rows.append([
            InlineKeyboardButton(text=f"🕒 Кулдаун: {cooldown} сек.", callback_data="enter_auto_bump_items_cooldown")
        ])
        param_rows.append([
            InlineKeyboardButton(text="📊 Позиции товаров", callback_data=calls.BumpItemsPositionsPagination(page=0).pack())
        ])
    else:
        if night["enabled"]:
            param_rows = [
                [
                InlineKeyboardButton(text=f"⏰☀️ Днём: {interval} сек.", callback_data="enter_auto_bump_items_interval"),
                InlineKeyboardButton(text=f"⏰🌙 Ночью: {night_interval} сек.", callback_data="enter_auto_bump_items_night_interval")
                ],
                [
                InlineKeyboardButton(text=f"🕓 Ночь с: {night['time_from']}", callback_data="enter_auto_bump_items_night_time_from"),
                InlineKeyboardButton(text=f"🕗 Ночь по: {night['time_to']}", callback_data="enter_auto_bump_items_night_time_to")
                ]
            ]
        else:
            param_rows = [
                [InlineKeyboardButton(text=f"⏰ Интервал: {interval} сек.", callback_data="enter_auto_bump_items_interval")]
            ]

    rows = [
        [InlineKeyboardButton(text=f"⬆️ Поднять товары", callback_data="confirm_bump_items")],
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_auto_bump_items_enabled")],
        [InlineKeyboardButton(text=f"🔀 Способ: {mode}", callback_data="switch_auto_bump_items_mode")],
        [InlineKeyboardButton(text=f"📦 Поднимать: {all}", callback_data="switch_auto_bump_items_all")],
        [InlineKeyboardButton(text=f"🌙 Ночной режим: {night_enabled}", callback_data="switch_auto_bump_items_night_enabled")],
        *param_rows,
        [
        InlineKeyboardButton(text=f"➕ Включенные: {included}", callback_data=calls.IncludedBumpItemsPagination(page=0).pack()),
        InlineKeyboardButton(text=f"➖ Исключенные: {excluded}", callback_data=calls.ExcludedBumpItemsPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def bump_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⬆️ Авто-поднятие</b>
        \n{placeholder}
    """)
    return txt