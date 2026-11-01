from datetime import datetime
from logging import getLogger
from colorama import Fore

from settings import Settings as sett, BLACKLIST, set_json


logger = getLogger("universal.blacklist")


def _save(blacklist: dict) -> bool:
    try:
        set_json(BLACKLIST.path, blacklist)
        return True
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Не удалось сохранить чёрный список: {Fore.WHITE}{e}")
        return False


def get_blacklist() -> dict:
    return (sett.get("blacklist") or {}).get("users") or {}


def _find_key(users: dict, username: str | None) -> str | None:
    if not username:
        return None
    username = str(username).strip().lower()
    return next((key for key in users if key.lower() == username), None)


def get_blacklist_entry(username: str | None) -> dict | None:
    users = get_blacklist()
    key = _find_key(users, username)
    return {"username": key, **users[key]} if key else None


def is_blacklisted(username: str | None) -> bool:
    return _find_key(get_blacklist(), username) is not None


def add_to_blacklist(username: str, reason: str = "", by: str = "вручную") -> bool:
    username = str(username or "").strip().lstrip("@")
    if not username:
        return False

    blacklist = sett.get("blacklist") or {"users": {}}
    users = blacklist.setdefault("users", {})
    if _find_key(users, username):
        return False

    users[username] = {
        "reason": reason.strip(),
        "date": datetime.now().isoformat(),
        "by": by
    }
    if not _save(blacklist):
        return False
    logger.info(
        f"{Fore.LIGHTRED_EX}Покупатель {Fore.LIGHTWHITE_EX}{username} {Fore.LIGHTRED_EX}добавлен в чёрный список"
        f"{Fore.WHITE}{f' ({by})' if by else ''}{f': {reason.strip()}' if reason.strip() else ''}"
    )
    return True


def remove_from_blacklist(username: str) -> bool:
    blacklist = sett.get("blacklist") or {"users": {}}
    users = blacklist.setdefault("users", {})
    key = _find_key(users, username)
    if not key:
        return False

    del users[key]
    if not _save(blacklist):
        return False
    logger.info(f"{Fore.LIGHTGREEN_EX}Покупатель {Fore.LIGHTWHITE_EX}{key} {Fore.LIGHTGREEN_EX}убран из чёрного списка")
    return True
