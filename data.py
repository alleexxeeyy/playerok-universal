import json
import os
from datetime import datetime

DATA = {
    "initialized_users": {
        "path": "bot_data/initialized_users.json",
        "default": []
    }
}

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
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = default
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    finally:
        return config
    
def set_json(path: str, new: dict):
    """
    Устанавливает новые данные в файл данных.

    :param path: Путь к json файлу.
    :type path: `str`

    :param new: Новые данные.
    :type new: `dict`
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(new, f, indent=4, ensure_ascii=False)

class Data:

    @staticmethod
    def get(name, data: dict | None = None) -> dict:
        data = data if data is not None else DATA
        if name not in data:
            return None
        return get_json(data[name]["path"], data[name]["default"])

    @staticmethod
    def set(name, new, data: dict | None = None) -> dict:
        data = data if data is not None else DATA
        if name not in data:
            return None
        set_json(data[name]["path"], new)