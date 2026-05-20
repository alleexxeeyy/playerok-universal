import os
import requests
import zipfile
import io
import shutil
import asyncio
from colorama import Fore
from logging import getLogger
from packaging.version import Version

from tgbot.telegrambot import (
    get_telegram_bot as tgbot, 
    get_telegram_bot_loop as tgbot_loop
)
from tgbot.templates import (
    new_release_text, 
    new_release_kb
)
from settings import Settings as sett

from __init__ import VERSION
from core.utils import restart


REPO = "alleexxeeyy/playerok-universal"
logger = getLogger("universal.updater")

latest_release = None


def get_releases():
    response = requests.get(f"https://api.github.com/repos/{REPO}/releases", timeout=5)
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
        raise Exception(f"Ошибка при скачивании архива обновления: {zip_response.status_code}")
    
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
        global latest_release
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
            
            config = sett.get("config")
            if not config["updates"]["auto_update"]:
                logger.info(f"{Fore.WHITE}Пропускаю установку обновления, согласно настройкам конфига")
                return
            
            logger.info(f"Загружаю обновление {latest_release['tag_name']}...")
            bytes = download_update(latest_release)
            if not bytes:
                return
            
            logger.info(f"Устанавливаю обновление {latest_release['tag_name']}...")
            if install_update(latest_release, bytes):
                logger.info(f"{Fore.YELLOW}Обновление {Fore.LIGHTWHITE_EX}{latest_release['tag_name']} {Fore.YELLOW}было успешно установлено.")
                restart()
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обновлении: {Fore.WHITE}{e}")


async def check_new_releases_task(interval=180):
    while True:
        await asyncio.sleep(interval)
        try:
            global latest_release

            releases = get_releases()
            release = get_latest_release(releases)
            
            if (
                latest_release and latest_release == release
                or Version(VERSION) >= Version(release["tag_name"])
            ):
                continue

            latest_release = release

            config = sett.get("config")
            if not config["updates"]["notify"]:
                continue

            bot = tgbot().bot
            for user_id in config["telegram"]["bot"]["signed_users"]: 
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(
                        chat_id=user_id,
                        text=new_release_text(release),
                        reply_markup=new_release_kb(),
                        disable_web_page_preview=True,
                        parse_mode="HTML"
                    ), 
                    tgbot_loop()
                )
        except:
            pass