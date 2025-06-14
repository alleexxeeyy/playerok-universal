import json
import os

class Data:
    INITIALIZED_USERS_PATH = 'plbot/bot_data/initialized_users.json'

    @staticmethod
    def get_initialized_users() -> list[str]:
        """ Получает содержимое initialized_users.json """
        folder_path = os.path.dirname(Data.INITIALIZED_USERS_PATH)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        try:
            with open(Data.INITIALIZED_USERS_PATH, 'r', encoding="utf-8") as f:
                initialized_users = json.load(f)
        except:
            with open(Data.INITIALIZED_USERS_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            initialized_users = []
        finally:
            return initialized_users

    @staticmethod
    def set_initialized_users(new_data):
        """ Перезаписывает данные в initialized_users.json """
        with open(Data.INITIALIZED_USERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)