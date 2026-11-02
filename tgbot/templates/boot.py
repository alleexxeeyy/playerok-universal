import html
import time
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION
from .. import callback_datas as calls


REPORT_BUDGET = 3600 # лимит Telegram — 4096 символов вместе с разметкой, оставляем запас на шапку и подвал
BOOT_STAGES = {
    "load": ("❌", "не загрузился"),
    "start": ("⚠️", "ошибка при запуске"),
    "disabled": ("🔴", "выключился")
}


def boot_report_text(marker: dict | None, errors: list[dict], working: int, total: int):
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
        size = sum(len(line) + 1 for line in lines)
        shown = 0
        for error in errors:
            emoji, stage = BOOT_STAGES.get(error["stage"], ("⚠️", "ошибка"))
            block = [
                f"{emoji} <b>{html.escape(error['module'])}</b> — {stage}",
                f"<blockquote>{error['text']}</blockquote>"
            ]
            block_size = sum(len(line) + 1 for line in block)
            if size + block_size > REPORT_BUDGET:
                break
            lines += block
            size += block_size
            shown += 1
        if len(errors) > shown:
            lines.append(f"...и ещё {len(errors) - shown} — смотрите logs/latest.log")
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
