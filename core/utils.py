import os
import sys
import ctypes
import logging
from colorlog import ColoredFormatter
from colorama import Fore
import pkg_resources
import subprocess
import requests
import random
import time
from logging import getLogger
logger = getLogger(f"universal.core")



def restart():
    """Перезагружает консоль."""
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()


def set_title(title: str):
    """
    Устанавливает заголовок консоли.

    :param title: Заголовок.
    :type title: `str`
    """
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif sys.platform.startswith("linux"):
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()
    elif sys.platform == "darwin":
        sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()


def setup_logger(log_file: str = "logs/latest.log"):
    """
    Настраивает логгер.

    :param log_file: Путь к файлу логов.
    :type log_file: `str`
    """
    class ShortLevelFormatter(ColoredFormatter):
        def format(self, record):
            record.shortLevel = record.levelname[0]
            return super().format(record)

    os.makedirs("logs", exist_ok=True)
    LOG_FORMAT = "%(light_black)s%(asctime)s · %(log_color)s%(shortLevel)s: %(reset)s%(white)s%(message)s"
    formatter = ShortLevelFormatter(
        LOG_FORMAT,
        datefmt="%d.%m.%Y %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'light_blue',
            'INFO': 'light_green',
            'WARNING': 'yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'red',
        },
        style='%'
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-1s · %(name)-20s %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
    

def is_package_installed(requirement_string: str) -> bool:
    """
    Проверяет, установлена ли библиотека.

    :param requirement_string: Строка пакета из файла зависимостей.
    :type requirement_string: `str`
    """
    try:
        pkg_resources.require(requirement_string)
        return True
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        return False


def install_requirements(requirements_path: str):
    """
    Устанавливает зависимости из файла.

    :param requirements_path: Путь к файлу зависимостей.
    :type requirements_path: `str`
    """
    if not os.path.exists(requirements_path):
        return
    with open(requirements_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    missing_packages = []
    for line in lines:
        pkg = line.strip()
        if not pkg or pkg.startswith("#"):
            continue
        if not is_package_installed(pkg):
            missing_packages.append(pkg)
    if missing_packages:
        logger.info(f"Установка недостающих зависимостей: {Fore.YELLOW}{f'{Fore.WHITE}, {Fore.YELLOW}'.join(missing_packages)}{Fore.WHITE}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])


def patch_requests():
    """Патчит стандартные requests на кастомные с обработкой ошибок."""
    _orig_request = requests.Session.request
    def _request(self, method, url, **kwargs):  # type: ignore
        for attempt in range(6):
            resp = _orig_request(self, method, url, **kwargs)
            try:
                text_head = (resp.text or "")[:1200]
            except Exception:
                text_head = ""
            statuses = {
                "429": "Too Many Requests",
                "502": "Bad Gateway",
                "503": "Service Unavailable"
            }
            if str(resp.status_code) not in statuses:
                for status in statuses.values():
                    if status in text_head:
                        break
                else: 
                    return resp
            retry_hdr = resp.headers.get("Retry-After")
            try:
                delay = float(retry_hdr) if retry_hdr else min(120.0, 5.0 * (2 ** attempt))
            except Exception:
                delay = min(120.0, 5.0 * (2 ** attempt))
            delay += random.uniform(0.2, 0.8)  # небольшой джиттер
            time.sleep(delay)
        return resp
    requests.Session.request = _request  # type: ignore