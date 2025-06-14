import os
import requests
import zipfile
import io
import shutil
import sys
from colorama import Fore

from core.console import restart
from bot_settings.app import CURRENT_VERSION, SKIP_UPDATES

class Updater:
    """ Класс-обновлятор бота. """

    REPO = "alleexxeeyy/playerok-universal"
    API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

    @staticmethod
    def check_for_updates():
        """ Проверяет бота на наличие обновлений на GitHub. """
        try:
            response = requests.get(Updater.API_URL)
            if response.status_code != 200:
                raise Exception(f"Ошибка запроса к GitHub API: {response.status_code}")
            
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            if latest_version == CURRENT_VERSION:
                print(f"{Fore.WHITE}У вас установлена последняя версия: {Fore.LIGHTWHITE_EX}{CURRENT_VERSION}\n")
                return False
            print(f"\n{Fore.LIGHTYELLOW_EX}Доступна новая версия: {Fore.LIGHTWHITE_EX}{latest_version}")
            if SKIP_UPDATES:
                print(f"{Fore.WHITE}Пропускаем установку обновления. Если вы хотите автоматически скачивать обновления, измените значение "
                      f"{Fore.LIGHTWHITE_EX}SKIP_UPDATES{Fore.WHITE} на {Fore.LIGHTYELLOW_EX}False {Fore.WHITE}в файле настроек {Fore.LIGHTWHITE_EX}(bot_settings/app.py)\n")
                return
            
            print(f"{Fore.WHITE}Скачиваем: {Fore.LIGHTWHITE_EX}{latest_release['html_url']}\n")
            print(f"{Fore.WHITE}Загружаю обновление...")
            bytes = Updater.download_update(latest_release)
            if bytes:
                print(f"{Fore.WHITE}Устанавливаю обновление...")
                if Updater.install_update(bytes):
                    print(f"\n{Fore.LIGHTYELLOW_EX}✅ Обновление {Fore.LIGHTWHITE_EX}{latest_version} {Fore.LIGHTYELLOW_EX}было успешно установлено.")
                    restart()
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}При проверке на наличие обновлений произошла ошибка: {Fore.WHITE}{e}")
        return False

    @staticmethod
    def download_update(release_info: str):
        """ Скачивает архив с обновлением. """
        try:
            zip_url = release_info['zipball_url']
            zip_response = requests.get(zip_url)
            if zip_response.status_code != 200:
                raise Exception(f"{Fore.LIGHTRED_EX}При скачивании архива обновления произошла ошибка: {zip_response.status_code}")
            return zip_response.content
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}При скачивании обновления произошла ошибка: {Fore.WHITE}{e}")
            return False
    
    @staticmethod
    def install_update(zip_response_content: bytes):
        """Устанавливает обновление."""
        temp_dir = ".temp_update"
        try:
            with zipfile.ZipFile(io.BytesIO(zip_response_content), 'r') as zip_ref:
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
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}При установке обновления произошла ошибка: {Fore.WHITE}{e}")
            return False
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)