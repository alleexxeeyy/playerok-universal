"""Notify the bot owner about startup failures without changing saved settings."""

import logging
import time

from proxy_utils import requests_proxy


logger = logging.getLogger("universal")


def deliver_startup_alert(config: dict, problem: str, send=None, pause=None,
                          message: str | None = None, retry: bool = True) -> bool:
    """Send an owner notice, optionally retrying until delivery succeeds."""
    token = config["telegram"]["api"]["token"]
    recipients = config["telegram"]["bot"]["signed_users"]
    if not recipients:
        chat_id = config["playerok"]["notifications"]["chat_id"]
        recipients = [chat_id] if chat_id else []
    if not token or not recipients:
        return False

    if send is None:
        from requests import post
        send = post
    if pause is None:
        pause = time.sleep

    api_url = config["telegram"]["api"]["custom_api_url"] or "https://api.telegram.org"
    if "://" not in api_url:
        api_url = "https://" + api_url
    url = f"{api_url.rstrip('/')}/bot{token}/sendMessage"
    telegram_proxy = config["telegram"]["api"]["proxy"]
    proxies = None
    if telegram_proxy:
        proxy_url = requests_proxy(telegram_proxy)
        proxies = {"http": proxy_url, "https": proxy_url}

    message = message or (
        f"⚠️ Playerok Universal остановлен. {problem}\n\n"
        "Cookie-данные, User-Agent и прокси сохранены. Проверьте прокси и обновите "
        "Cookie-данные через pluniversal setup. При необходимости переустановите бота "
        "с новыми настройками и восстановите резервную копию."
    )
    while True:
        for chat_id in recipients:
            # A failed Telegram proxy must not also block the emergency alert.
            for active_proxies in ([proxies, None] if proxies else [None]):
                try:
                    response = send(
                        url,
                        json={"chat_id": chat_id, "text": message},
                        proxies=active_proxies,
                        timeout=10,
                    )
                    if response.ok and response.json().get("ok") is True:
                        return True
                except Exception:
                    pass
        if not retry:
            return False
        logger.warning("Telegram недоступен; повторю отправку уведомления через 60 секунд.")
        pause(60)


def deliver_restart_started(config: dict, send=None) -> bool:
    """Confirm restart before checking Playerok."""
    message = "✅ Бот был успешно перезагружен.\n⏳ Проверяю подключение к Playerok…"
    return deliver_startup_alert(config, "", send=send, message=message, retry=False)


def deliver_playerok_connected(config: dict, send=None) -> bool:
    """Report a successful initial Playerok connection."""
    return deliver_startup_alert(config, "", send=send, message="✅ Playerok подключён.", retry=False)


def deliver_playerok_recovery(config: dict, send=None) -> bool:
    """Tell the owner that the Playerok proxy check succeeds again."""
    message = (
        "✅ Прокси Playerok снова отвечает на проверки. "
        "Если бот не получает сообщения или события, выполните /restart."
    )
    return deliver_startup_alert(config, "", send=send, message=message, retry=False)


def deliver_playerok_reconnected(config: dict, send=None) -> bool:
    """Tell the owner that Playerok itself resumed after a failed startup."""
    message = "✅ Playerok подключён. Работа восстановлена, /restart не требуется."
    return deliver_startup_alert(config, "", send=send, message=message, retry=False)


def deliver_playerok_alert(config: dict, problem: str, send=None) -> bool:
    """Warn the owner while keeping Telegram control available."""
    if problem == "Прокси Playerok не отвечает.":
        message = (
            "⚠️ Playerok пока недоступен: прокси не отвечает.\n\n"
            "Telegram-бот продолжает работать и автоматически повторит подключение. "
            "Если прокси больше не работает, замените его в /start → «Соединение» → «Прокси для Playerok». "
            "Настройки и Cookie-данные сохранены."
        )
        return deliver_startup_alert(config, problem, send=send, message=message, retry=False)

    retrying = problem in (
        "Прокси Playerok не отвечает.",
        "Не удалось подключиться к аккаунту Playerok. Проверьте Cookie-данные и прокси.",
    )
    if retrying:
        instructions = (
            "Telegram-бот продолжает работать. Бот повторит подключение к Playerok автоматически. "
            "Если прокси больше не работает, замените его: /start → Соединение → Прокси для Playerok. "
            "Если проблема в Cookie-данных, обновите их в разделе Авторизация. "
        )
    else:
        instructions = (
            "Telegram-бот продолжает работать. Проверьте прокси: /start → Соединение → "
            "Прокси для Playerok. Если после восстановления сообщения или события не приходят, "
            "выполните /restart. При проблеме с Cookie-данными обновите их в разделе Авторизация. "
        )
    message = f"⚠️ Playerok недоступен: {problem}\n\n{instructions}Сохранённые настройки и данные не удалены."
    return deliver_startup_alert(config, problem, send=send, message=message, retry=False)
