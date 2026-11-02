import html
import time
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION
from .. import callback_datas as calls


BOOT_STAGES = {
    "load": ("❌", "не загрузился"),
    "start": ("⚠️", "ошибка при запуске"),
    "disabled": ("🔴", "выключился")
}


def boot_report_text(marker: dict | None, errors: list[dict], errors_total: int, working: int, total: int):
    marker = marker or {}
    reason = marker.get("reason")
    took = f" за {int(time.time() - marker['time'])} сек" if marker.get("time") else ""

    if reason == "update":
        lines = [f"✅ Бот <b>обновлён до v{VERSION}</b>{took}"]
    elif reason:
        lines = [f"✅ Бот <b>успешно перезагружен</b>{took}"]
    else:
        lines = ["⚠️ Бот запущен, но <b>есть проблемы</b>"]

    if total:
        lines.append(f"🔌 Модули: работают <b>{working}</b> из <b>{total}</b>")

    if errors:
        lines.append("")
        for error in errors:
            emoji, stage = BOOT_STAGES.get(error["stage"], ("⚠️", "ошибка"))
            lines.append(f"{emoji} <b>{html.escape(error['module'])}</b> — {stage}")
            lines.append(f"<blockquote>{error['text']}</blockquote>")
        if errors_total > len(errors):
            lines.append(f"...и ещё {errors_total - len(errors)} — смотрите logs/latest.log")
        lines.append("")
        lines.append("Нажмите на модуль ниже, чтобы получить полный текст ошибки — его можно переслать разработчику")

    return "\n".join(lines)


def boot_report_kb(errors: list[dict], boot_id: int):
    rows = [
        [InlineKeyboardButton(
            text=f"📄 {error['module']} — полная ошибка",
            callback_data=calls.BootErrorFile(boot=boot_id, idx=i).pack()
        )]
        for i, error in enumerate(errors)
    ]
    rows.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
