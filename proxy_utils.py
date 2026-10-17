"""Proxy configuration shared by Playerok, Telegram and setup checks."""

from urllib.parse import urlsplit, unquote


def normalize_proxy(proxy: str) -> str:
    """Keep old scheme-less proxies working as HTTP proxies."""
    if not proxy:
        return ""
    proxy = proxy.strip()
    if "://" in proxy:
        scheme, address = proxy.split("://", 1)
        return f"{scheme.lower()}://{address}"
    return f"http://{proxy}"


def parse_proxy(proxy: str):
    """Return a validated proxy URL, or raise ValueError."""
    url = urlsplit(normalize_proxy(proxy))
    if url.scheme not in ("http", "socks5") or not url.hostname or any(c.isspace() for c in proxy):
        raise ValueError("Поддерживаются только HTTP и SOCKS5 прокси")
    try:
        port = url.port
    except ValueError as exc:
        raise ValueError("Некорректный порт прокси") from exc
    if not port or not 1 <= port <= 65535 or url.path or url.query or url.fragment:
        raise ValueError("Некорректный адрес прокси")
    if (url.username is None) != (url.password is None) or (url.username is not None and not url.username) or (url.password is not None and not url.password):
        raise ValueError("Нужны имя пользователя и пароль прокси")
    return url


def requests_proxy(proxy: str) -> str:
    """Resolve hostnames at the SOCKS server when using requests/curl."""
    url = normalize_proxy(proxy)
    return "socks5h://" + url[len("socks5://"):] if url.startswith("socks5://") else url


class ProxyCheckState:
    """Track failures and report transitions for one Playerok proxy."""

    def __init__(self):
        self.failures = 0
        self.unavailable = False

    def record(self, working: bool, threshold: int) -> str | None:
        if working:
            self.failures = 0
            if self.unavailable:
                self.unavailable = False
                return "recovered"
            return None

        self.failures += 1
        if self.failures >= threshold and not self.unavailable:
            self.unavailable = True
            return "unavailable"
        return None


def websocket_proxy_options(proxy: str) -> dict:
    url = parse_proxy(proxy)
    options = {
        "http_proxy_host": url.hostname,
        "http_proxy_port": url.port,
        "proxy_type": "socks5h" if url.scheme == "socks5" else "http",
    }
    if url.username is not None:
        options["http_proxy_auth"] = (unquote(url.username), unquote(url.password))
    return options
