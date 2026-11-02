import re
import json
import requests
from logging import getLogger

from settings import Settings as sett


logger = getLogger("universal.notify")

TOKEN_RE = re.compile(r"/bot[^/\s]+/")

# подключение к Telegram, выбранное при запуске — может отличаться от конфига, если прокси отвалился
_connection: dict | None = None


def set_connection(proxy: str, custom_api_url: str):
    global _connection
    _connection = {"proxy": proxy or "", "custom_api_url": custom_api_url or ""}


def get_connection() -> dict:
    if _connection is not None:
        return _connection
    api = sett.get("config")["telegram"]["api"]
    return {"proxy": api["proxy"], "custom_api_url": api["custom_api_url"]}


def api_base(custom_api_url: str) -> str:
    if not custom_api_url:
        return "https://api.telegram.org"
    if not custom_api_url.startswith(("http://", "https://")):
        custom_api_url = "https://" + custom_api_url
    return custom_api_url.rstrip("/")


def proxies(proxy: str) -> dict | None:
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None


def _dump_kb(kb) -> str | None:
    if kb is None:
        return None
    if hasattr(kb, "model_dump"):
        kb = kb.model_dump(exclude_none=True)
    return json.dumps(kb, ensure_ascii=False)


def call(method: str, data: dict = None, files: dict = None, timeout: tuple = (5, 20)) -> dict | bool | None:
    try:
        token = sett.get("config")["telegram"]["api"]["token"]
        if not token:
            return None

        conn = get_connection()
        resp = requests.post(
            f"{api_base(conn['custom_api_url'])}/bot{token}/{method}",
            data={k: v for k, v in (data or {}).items() if v is not None},
            files=files,
            proxies=proxies(conn["proxy"]),
            timeout=timeout
        )
        result = resp.json()
        if not result.get("ok"):
            logger.debug(f"Telegram не принял {method}: {result.get('description')}")
            return None
        return result.get("result")
    except Exception as e:
        logger.debug(f"Не удалось выполнить {method} в Telegram: {TOKEN_RE.sub('/bot***/', str(e))}")
        return None


def send_message(chat_id: int, text: str, kb=None) -> int | None:
    result = call("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
        "reply_markup": _dump_kb(kb)
    })
    return result.get("message_id") if isinstance(result, dict) else None


def edit_message(chat_id: int, message_id: int, text: str, kb=None) -> bool:
    return call("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
        "reply_markup": _dump_kb(kb)
    }) is not None


def send_document(chat_id: int, filename: str, content: bytes, caption: str = None) -> bool:
    return call(
        "sendDocument",
        {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
        files={"document": (filename, content)},
        timeout=(5, 60)
    ) is not None


def signed_users() -> list[int]:
    try:
        return list(sett.get("config")["telegram"]["bot"]["signed_users"])
    except Exception:
        return []
