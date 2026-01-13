import os
import requests
import zipfile
import io
import shutil
from colorama import Fore
from logging import getLogger
from packaging.version import Version

from __init__ import VERSION, SKIP_UPDATES
from core.utils import restart


REPO = "alleexxeeyy/playerok-universal"
logger = getLogger("universal.updater")


def get_releases():
    response = requests.get(f"https://api.github.com/repos/{REPO}/releases")
    response.raise_for_status()
    if response.status_code != 200:
        raise Exception(f"Ошибка запроса к GitHub API: {response.status_code}")
    return response.json()


def get_latest_release(releases):
    latest = None
    latest_rel = None
    for rel in releases:
        tag_name = rel["tag_name"]
        if latest is None:
            latest = Version(tag_name)
            latest_rel = rel
        if Version(tag_name) > latest:
            latest = Version(tag_name)
            latest_rel = rel
    return latest_rel


def download_update(release_info: dict) -> bytes:
    zip_url = release_info['zipball_url']
    zip_response = requests.get(zip_url)
    if zip_response.status_code != 200:
        raise Exception(f"При скачивании архива обновления произошла ошибка: {zip_response.status_code}")
    return zip_response.content


def install_update(release_info: dict, content: bytes) -> bool:
    temp_dir = ".temp_update"
    try:
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            archive_root = None
            for item in os.listdir(temp_dir):
                if os.path.isdir(os.path.join(temp_dir, item)):
                    archive_root = os.path.join(temp_dir, item)
                    break
            if not archive_root:
                raise Exception("В архиве нет корневой папки!")
            for root, _, files in os.walk(archive_root):
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join('.', os.path.relpath(src, archive_root))
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
            return True
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def check_for_updates():
    try:
        releases = get_releases()
        latest_release = get_latest_release(releases)
        versions = [release["tag_name"] for release in releases]
        
        if VERSION not in versions:
            logger.info(f"Вашей версии {Fore.LIGHTWHITE_EX}{VERSION} {Fore.WHITE}нету в релизах репозитория. Последняя версия: {Fore.LIGHTWHITE_EX}{latest_release['tag_name']}")
            return
        elif Version(VERSION) == Version(latest_release["tag_name"]):
            logger.info(f"У вас установлена последняя версия: {Fore.LIGHTWHITE_EX}{VERSION}")
            return
        elif Version(VERSION) < Version(latest_release["tag_name"]):
            logger.info(f"{Fore.YELLOW}Доступна новая версия: {Fore.LIGHTWHITE_EX}{latest_release['tag_name']}")
            if SKIP_UPDATES:
                logger.info(
                    f"Пропускаю установку обновления. Если вы хотите автоматически скачивать обновления, измените значение "
                    f"{Fore.LIGHTWHITE_EX}SKIP_UPDATES{Fore.WHITE} на {Fore.YELLOW}False {Fore.WHITE}в файле инициализации {Fore.LIGHTWHITE_EX}(__init__.py)"
                )
                return
            
            logger.info(f"Загружаю обновление {latest_release['tag_name']}...")
            bytes = download_update(latest_release)
            if not bytes:
                print("no bytes")
                return
            logger.info(f"Устанавливаю обновление {latest_release['tag_name']}...")
            if install_update(latest_release, bytes):
                logger.info(f"{Fore.YELLOW}Обновление {Fore.LIGHTWHITE_EX}{latest_release['tag_name']} {Fore.YELLOW}было успешно установлено.")
                restart()
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обновлении: {Fore.WHITE}{e}")