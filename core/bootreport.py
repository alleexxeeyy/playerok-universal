import os
import re
import sys
import time
import html
import logging
import platform
from logging import getLogger

from data import Data as data, SYSTEM_DATA, BOOT_MARKER


logger = getLogger("universal.bootreport")

MARKER_TTL = 15 * 60
LOG_TAIL_SIZE = 512 * 1024
MAX_REPORT_ERRORS = 10
BOT_PACKAGES = ("core", "plbot", "tgbot", "playerokapi", "settings", "data", "utils", "updater")
MODULE_META_FIELDS = ("PREFIX", "VERSION", "NAME", "DESCRIPTION", "AUTHORS", "LINKS")
NETWORK_ERRORS = (
    "ConnectionError", "ConnectTimeout", "ReadTimeout", "Timeout", "ProxyError",
    "ClientConnectorError", "ServerDisconnectedError", "TimeoutError"
)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

boot_id = int(time.time()) % 100000 # чтобы кнопки из отчёта прошлого запуска не отдавали чужие ошибки
started_at = time.time()

_errors: list[dict] = []
_module_logs: dict[str, list[str]] = {}
_capturing = False
_log_handler = None


class _ModuleLogHandler(logging.Handler):
    def emit(self, record):
        if record.levelno < logging.ERROR:
            return
        try:
            text = ANSI_RE.sub("", record.getMessage()).strip()
        except Exception:
            return
        if text:
            _module_logs.setdefault(record.name, []).append(text)


def start_capture():
    global _capturing, _log_handler
    _capturing = True
    if _log_handler is None:
        _log_handler = _ModuleLogHandler()
        logging.getLogger().addHandler(_log_handler)


def stop_capture():
    global _capturing, _log_handler
    _capturing = False
    if _log_handler is not None:
        logging.getLogger().removeHandler(_log_handler)
        _log_handler = None


def is_capturing() -> bool:
    return _capturing


def get_errors() -> list[dict]:
    return _errors


def module_of(func) -> str | None:
    name = getattr(func, "__module__", "") or ""
    if name.startswith("modules."):
        return name.split(".")[1]
    return None


def add_error(module: str, stage: str, trace: str, text: str = None):
    if not _capturing:
        return
    last = _last_line(trace)
    for error in _errors:
        if error["module"] == module and error["stage"] == stage and _last_line(error["trace"]) == last:
            return
    _errors.append({
        "module": module,
        "stage": stage,
        "text": text or explain_error(trace),
        "trace": trace
    })


def _last_line(trace: str) -> str:
    lines = [line.strip() for line in (trace or "").strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""


def explain_error(trace: str) -> str:
    last = _last_line(trace)
    low = (trace or "").lower()
    esc = html.escape

    match = re.search(r"No module named '([^']+)'", last)
    if match:
        root = match.group(1).split(".")[0]
        if root in BOT_PACKAGES:
            return "Модулю нужна более новая версия бота — обновите бота"
        if root == "modules":
            return "В модуле не хватает файлов — переустановите модуль"
        return f"Не установлена библиотека <b>{esc(root)}</b>, которая нужна модулю"

    match = re.search(r"cannot import name '([^']+)' from '([^']+)'", last)
    if match:
        root = match.group(2).split(".")[0]
        if root in BOT_PACKAGES:
            return "Модулю нужна более новая версия бота — обновите бота"
        return f"Несовместимая версия библиотеки <b>{esc(root)}</b>"

    if "pyarmor" in low:
        return (
            "Ошибка защищённого модуля (PyArmor). Чаще всего модуль собран под другую версию Python — "
            f"у вас Python {sys.version_info.major}.{sys.version_info.minor}, {esc(platform.system())}"
            f"\n<code>{esc(last[:200])}</code>"
        )

    if last.startswith(("SyntaxError", "IndentationError", "TabError")):
        return "В файле модуля синтаксическая ошибка — файл повреждён, переустановите модуль"

    match = re.search(r"has no attribute '([^']+)'", last)
    if match and match.group(1) in MODULE_META_FIELDS and "module 'modules." in last:
        return f"Это не модуль Playerok Universal — нет обязательного поля <b>{esc(match.group(1))}</b>"

    exc_name = last.split(":", 1)[0].rsplit(".", 1)[-1]
    if exc_name in NETWORK_ERRORS:
        return "Не удалось связаться с сервером — проверьте интернет и прокси"

    if exc_name == "PermissionError":
        return "Нет прав на файлы бота — проверьте права на папку бота"

    return esc(last[:300]) or "Неизвестная ошибка"


def collect_disabled(modules: list):
    # официальные плагины ловят свою ошибку сами, пишут critical и выключаются — ядро об этом не узнаёт
    for module in modules:
        if module.enabled or any(e["module"] == module._dir_name for e in _errors):
            continue
        prefix = ANSI_RE.sub("", module.meta.prefix or "").strip()
        lines = []
        for line in _module_logs.get(module.meta.name, []):
            if prefix and line.startswith(prefix):
                line = line[len(prefix):].strip()
            if line:
                lines.append(line)
        trace = "\n".join(lines)
        text = html.escape(" · ".join(lines)[:300]) if lines else "Модуль выключился при запуске, причину не сообщил"
        add_error(module._dir_name, "disabled", trace or text, text)


def set_marker(reason: str, chat_id: int = None, message_id: int = None, **extra):
    os.makedirs(os.path.dirname(BOOT_MARKER.path), exist_ok=True)
    data.set("boot_marker", {
        "reason": reason,
        "chat_id": chat_id,
        "message_id": message_id,
        "time": time.time(),
        **extra
    }, SYSTEM_DATA)


def has_marker() -> bool:
    marker = data.get("boot_marker", SYSTEM_DATA) or {}
    return bool(marker) and time.time() - marker.get("time", 0) < MARKER_TTL


def pop_marker() -> dict | None:
    marker = data.get("boot_marker", SYSTEM_DATA) or {}
    if marker:
        data.set("boot_marker", {}, SYSTEM_DATA)
    if not marker or time.time() - marker.get("time", 0) >= MARKER_TTL:
        return None
    return marker


def _deliver(marker: dict | None, text: str, kb, to_all: bool):
    from core import notify

    initiator = (marker or {}).get("chat_id")
    if initiator:
        message_id = (marker or {}).get("message_id")
        if not (message_id and notify.edit_message(initiator, message_id, text, kb)):
            notify.send_message(initiator, text, kb)

    if to_all or not initiator:
        for user_id in notify.signed_users():
            if user_id != initiator:
                notify.send_message(user_id, text, kb)


def wait_telegram_bot(timeout: int = 60):
    # хуки ON_TELEGRAM_BOT_INIT отрабатывают в потоке ТГ-бота — ждём их, чтобы ошибки попали в отчёт
    from tgbot.telegrambot import get_telegram_bot

    deadline = time.time() + timeout
    while time.time() < deadline:
        if getattr(get_telegram_bot(), "me", None):
            return
        time.sleep(0.5)


def send_report(modules: list):
    try:
        wait_telegram_bot()
        from tgbot import templates as templ

        marker = pop_marker()
        collect_disabled(modules)
        stop_capture()

        if not marker and not _errors:
            return

        working = len([module for module in modules if module.enabled])
        total = len(modules) + len({e["module"] for e in _errors if e["stage"] == "load"})
        text = templ.boot_report_text(marker, _errors[:MAX_REPORT_ERRORS], len(_errors), working, total)
        kb = templ.boot_report_kb(_errors[:MAX_REPORT_ERRORS], boot_id)
        _deliver(marker, text, kb, to_all=bool(_errors))
    except Exception as e:
        stop_capture()
        logger.error(f"Не удалось отправить отчёт о запуске в Telegram: {e}")


def _log_tail(path: str = "logs/latest.log") -> bytes | None:
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > LOG_TAIL_SIZE:
                f.seek(size - LOG_TAIL_SIZE)
                f.readline()
            return f.read()
    except Exception:
        return None


def notify_crash(trace: str, reason: str = None):
    # тут не трогаем tgbot — падение могло случиться как раз на его импорте
    try:
        from core import notify

        text = (
            "❌ <b>Бот не смог запуститься</b>"
            f"\n\n<blockquote>{reason or explain_error(trace)}</blockquote>"
            "\n\nЛог запуска — в файле ниже. Частые ошибки и их решения: devfried.com/docs/faq/"
        )
        marker = pop_marker()
        _deliver(marker, text, None, to_all=True)

        log = _log_tail()
        if not log:
            return
        recipients = notify.signed_users()
        initiator = (marker or {}).get("chat_id")
        if initiator and initiator not in recipients:
            recipients.append(initiator)
        for user_id in recipients:
            notify.send_document(user_id, "latest.log", log)
    except Exception as e:
        logger.debug(f"Не удалось сообщить о падении в Telegram: {e}")
