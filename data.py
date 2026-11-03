import copy
import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass


@dataclass
class DataFile:
    name: str
    path: str
    default: list | dict


INITIALIZED_USERS = DataFile(
    name="initialized_users",
    path="bot_data/initialized_users.json",
    default=[]
)
SAVED_ITEMS = DataFile(
    name="saved_items",
    path="bot_data/saved_items.json",
    default=[]
)
CACHED_ORDERS = DataFile(
    name="cached_orders",
    path="bot_data/cached_orders.json",
    default={}
)
BUMPED_ITEMS = DataFile(
    name="bumped_items",
    path="bot_data/bumped_items.json",
    default={}
)
DATA = [INITIALIZED_USERS, SAVED_ITEMS, CACHED_ORDERS, BUMPED_ITEMS]

# служебные файлы — не попадают в экспорт конфигов
BOOT_MARKER = DataFile(
    name="boot_marker",
    path="bot_data/boot_marker.json",
    default={}
)
OWNER_LINK = DataFile(
    name="owner_link",
    path="bot_data/owner_link.json",
    default={}
)
ACCESS_REQUESTS = DataFile(
    name="access_requests",
    path="bot_data/access_requests.json",
    default={}
)
DISABLED_MODULES = DataFile(
    name="disabled_modules",
    path="bot_data/disabled_modules.json",
    default=[]
)
SYSTEM_DATA = [BOOT_MARKER, OWNER_LINK, ACCESS_REQUESTS, DISABLED_MODULES]


def get_json(path: str, default: dict | list) -> dict:
    """
    Получает содержимое файла данных.
    Создаёт файл данных, если его нет.

    :param path: Путь к json файлу.
    :type path: `str`

    :param default: Стандартная структура файла.
    :type default: `dict`
    """
    folder_path = os.path.dirname(path)
    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for _ in range(3):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            break
        except (PermissionError, BlockingIOError, json.JSONDecodeError):
            # файл как раз подменяют или дописывают — читаем ещё раз, а не затираем данные
            time.sleep(0.1)
        except:
            break

    # битый файл не теряем молча: копия рядом, потом стандартная структура
    if os.path.exists(path):
        try: shutil.copyfile(path, f"{path}.bak")
        except: pass
    config = copy.deepcopy(default)
    try:
        set_json(path, config)
    except:
        pass
    return config
    

def set_json(path: str, new: dict):
    """
    Устанавливает новые данные в файл данных.

    :param path: Путь к json файлу.
    :type path: `str`

    :param new: Новые данные.
    :type new: `dict`
    """
    dir_name = os.path.dirname(path) or "."
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with tempfile.NamedTemporaryFile( # атомарная запись файла
        "w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        json.dump(new, tmp, ensure_ascii=False, indent=4)
        tmp.flush()
        os.fsync(tmp.fileno())

    os.replace(tmp.name, path)


class Data:
    
    @staticmethod
    def get(name: str, data: list[DataFile] = DATA) -> dict | list | None:
        try: 
            file = [file for file in data if file.name == name][0]
            return get_json(file.path, file.default)
        except: return None

    @staticmethod
    def set(name: str, new: list | dict, data: list[DataFile] = DATA):
        try: 
            file = [file for file in data if file.name == name][0]
            set_json(file.path, new)
        except: pass