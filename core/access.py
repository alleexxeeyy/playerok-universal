import os
import time
import secrets

from settings import Settings as sett
from data import Data as data, SYSTEM_DATA, OWNER_LINK


REQUEST_COOLDOWN = 24 * 60 * 60
CONFIRM_WORD = "подтверждаю"
OWNER_PREFIX = "owner_"


def get_signed_users() -> list[int]:
    return list(sett.get("config")["telegram"]["bot"]["signed_users"])


def is_signed(user_id: int) -> bool:
    return user_id in get_signed_users()


def add_signed_user(user_id: int) -> bool:
    config = sett.get("config")
    users = config["telegram"]["bot"]["signed_users"]
    if user_id in users:
        return False
    users.append(user_id)
    sett.set("config", config)
    forget_request(user_id)
    return True


def get_owner_code() -> str:
    # код лежит в файле, а не в памяти: ссылку печатает `pluniversal setup`, а принимает уже запущенный сервис
    os.makedirs(os.path.dirname(OWNER_LINK.path), exist_ok=True)
    link = data.get("owner_link", SYSTEM_DATA) or {}
    if not link.get("code"):
        link = {"code": secrets.token_urlsafe(16)}
        data.set("owner_link", link, SYSTEM_DATA)
    return link["code"]


def get_owner_link(bot_username: str) -> str:
    return f"https://t.me/{bot_username}?start={OWNER_PREFIX}{get_owner_code()}"


def claim_owner(user_id: int, code: str) -> bool:
    if get_signed_users():
        return False
    link = data.get("owner_link", SYSTEM_DATA) or {}
    if not link.get("code") or not secrets.compare_digest(link["code"].encode(), (code or "").encode()):
        return False
    data.set("owner_link", {}, SYSTEM_DATA)
    add_signed_user(user_id)
    return True


def is_legacy_password_login() -> bool:
    # бот настроили паролем на старой версии, но в ТГ так никто и не вошёл — пароль срабатывает один раз как ключ владельца
    config = sett.get("config")
    return not config["telegram"]["bot"]["signed_users"] and bool(config["telegram"]["bot"]["password"])


def _get_requests() -> dict:
    now = time.time()
    requests = data.get("access_requests", SYSTEM_DATA) or {}
    return {k: v for k, v in requests.items() if now - v.get("time", 0) < REQUEST_COOLDOWN}


def get_request(user_id: int) -> dict | None:
    return _get_requests().get(str(user_id))


def can_request_access(user_id: int) -> bool:
    return get_request(user_id) is None


def remember_request(user_id: int, username: str | None, name: str | None):
    requests = _get_requests()
    requests[str(user_id)] = {"time": time.time(), "username": username, "name": name}
    data.set("access_requests", requests, SYSTEM_DATA)


def forget_request(user_id: int):
    requests = _get_requests()
    if requests.pop(str(user_id), None) is not None:
        data.set("access_requests", requests, SYSTEM_DATA)
