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


def boot_report_text(marker: dict | None, errors: list[dict], working: int, total: int, notes: list[str] = None, disabled: int = 0):
    marker = marker or {}
    reason = marker.get("reason")

    if reason == "update":
        lines = [f"<b>✅ Бот обновлён до v{VERSION}</b>", ""]
    elif reason == "setup":
        lines = ["<b>✅ Playerok подключён, бот запущен</b>", ""]
    elif reason:
        lines = ["<b>✅ Бот успешно перезагружен</b>", ""]
    else:
        lines = ["<b>⚠️ Бот запущен, но есть проблемы</b>", ""]

    if reason and reason != "setup" and marker.get("time"):
        lines.append(f"<b>⏱ Время запуска:</b> {int(time.time() - marker['time'])} сек")
    if total:
        lines.append(f"<b>🔌 Модули:</b> работают {working} из {total}")
    if disabled:
        lines.append(f"<b>🔴 Выключено вами:</b> {disabled}")

    for note in notes or []:
        lines.append(f"<b>⚠️ Внимание:</b> <blockquote>{note}</blockquote>")

    if errors:
        lines += ["", "<b>🤬 Проблемы с модулями:</b>"]
        size = sum(len(line) + 1 for line in lines)
        shown = 0
        for error in errors:
            emoji, stage = BOOT_STAGES.get(error["stage"], ("⚠️", "ошибка"))
            block = f"<blockquote>{emoji} <b>{html.escape(error['module'])}</b> — {stage}\n{error['text']}</blockquote>"
            if size + len(block) + 1 > REPORT_BUDGET:
                break
            lines.append(block)
            size += len(block) + 1
            shown += 1
        if len(errors) > shown:
            lines.append(f"...и ещё {len(errors) - shown} — смотрите logs/latest.log")
        lines += ["", "❗ Нажмите на модуль ниже, чтобы получить полный текст ошибки — его можно переслать разработчику"]

    return "\n".join(lines).strip()


def boot_report_kb(errors: list[dict], boot_id: int):
    rows = []
    for i, error in enumerate(errors):
        file_cb = calls.BootErrorFile(boot=boot_id, idx=i).pack()
        if error["stage"] == "start": # модуль загрузился, но сломан — его можно выключить, чтобы не мешал
            rows.append([
                InlineKeyboardButton(text=f"📄 {error['module']}", callback_data=file_cb),
                InlineKeyboardButton(text="🔴 Отключить", callback_data=calls.BootModuleDisable(boot=boot_id, idx=i).pack())
            ])
        else:
            rows.append([InlineKeyboardButton(text=f"📄 {error['module']} — полная ошибка", callback_data=file_cb)])
    rows.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
