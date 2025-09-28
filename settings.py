import os
import json
import copy
from colorama import Fore, Style
from colorama.ansi import AnsiFore

DATA = {
    "config": {
        "path": "bot_settings/config.json",
        "default": {
            "playerok": {
                "api": {
                    "token": "",
                    "user_agent": "",
                    "proxy": "",
                    "requests_timeout": 30,
                    "listener_requests_delay": 4
                },
                "bot": {
                    "messages_watermark_enabled": True,
                    "messages_watermark": "©️ 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                    "read_chat_before_sending_message_enabled": True,
                    "first_message_enabled": True,
                    "custom_commands_enabled": True,
                    "auto_deliveries_enabled": True,
                    "auto_restore_items_enabled": True,
                    "auto_restore_items_priority_status": "DEFAULT",
                    "auto_complete_deals_enabled": True,
                    "tg_logging_enabled": True,
                    "tg_logging_chat_id": "",
                    "tg_logging_events": {
                        "new_user_message": True,
                        "new_system_message": True,
                        "new_deal": True,
                        "new_problem": True,
                        "deal_status_changed": True,
                    }
                }
            },
            "telegram": {
                "api": {
                    "token": ""
                },
                "bot": {
                    "password": "",
                    "signed_users": []
                }
            }
        },
        "params": {
            "playerok": {
                "api": {
                    "token": {
                        "required": True,
                        "type": str,
                        "desc": [
                            "Токен вашего аккаунта Playerok, который необходим для того, чтобы бот подключился и работал с вашим аккаунтом.",
                            "Его можно скопировать из cookie сайта playerok.com. Можете воспользоваться расширением Cookie-Editor."
                        ]
                    },
                    "user_agent": {
                        "required": False,
                        "type": str,
                        "desc": [
                            "Юзер агент вашего браузера. Желательно указать, чтобы бот лучше работал с вашим аккаунтом и возникало меньше проблем с подключением.",
                            "Узнать его просто: Переходите на сайт https://www.whatismybrowser.com/detect/what-is-my-user-agent/ и копируете весь текст в синем окошке."
                        ]
                    },
                    "proxy": {
                        "required": False,
                        "type": str,
                        "desc": [
                            "IPv4 прокси. Если желаете, можете указать его, тогда запросы будут отправляться с него.",
                            "Формат: user:pass@ip:port или ip:port"
                        ]
                    },
                    "requests_timeout": {
                        "required": False,
                        "type": int,
                        "desc": [
                            "Макс. время таймаут на подключение к playerok.com. Если у вас плохой интернет - указывайте значение больше. Указывается в секундах."
                        ]
                    },
                    "listener_requests_delay": {
                        "required": False,
                        "type": int,
                        "desc": [
                            "Периодичность отправления запросов на playerok.com для получения ивентов. Не рекомендуем ставить ниже 2, ",
                            "в виду повышенного риска блокировки вашего IP адреса со стороны Playerok. Указывается в секундах."
                        ]
                    }
                }
            },
            "telegram": {
                "api": {
                    "token": {
                        "required": True,
                        "type": str,
                        "desc": [
                            "Токен Telegram бота. В TG боте можно будет настроить остальную часть функционала бота.",
                            "Чтобы получить токен, нужно создать бота у @BotFather. Пишите /newbot и начинаете настройку."
                        ]
                    }
                },
                "bot": {
                    "password": {
                        "required": True,
                        "type": str,
                        "desc": [
                            "Пароль от вашего Telegram бота. Будет запрашиваться для использования бота."
                        ]
                    }
                }
            }
        }
    },
    "messages": {
        "path": "bot_settings/messages.json",
        "default": {
            "user_not_initialized": [
                "👋 Привет, {username}! Я бот-помощник 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                "",
                "🗨️ Если вы хотите поговорить с продавцом, напишите команду !продавец, чтобы я пригласил его в этот диалог.",
                "",
                "🕹️ А вообще, чтобы узнать все мои команды, напишите !команды"
            ], 
            "command_error": [
                "❌ При вводе команды произошла непредвиденная ошибка"
            ],
            "command_incorrect_use_error": [
                "❌ Неверное использование команды. Используйте {correct_use}"
            ],
            "buyer_command_commands": [
                "🕹️ Основные команды:",
                "┗ !продавец — уведомить и позвать продавца в этот чат"
            ],
            "buyer_command_seller": [
                "💬 Продавец был вызван в этот чат. Ожидайте, пока он подключиться к диалогу..."
            ],
            "deal_confirmed": [
                "🌟 Спасибо за успешную сделку. Буду рад, если оставите отзыв. Жду вас в своём магазине в следующий раз, удачи!"
            ]
        }
    },
    "custom_commands": {
        "path": "bot_settings/custom_commands.json",
        "default": {}
    },
    "auto_deliveries": {
        "path": "bot_settings/auto_deliveries.json",
        "default": []
    }
}


def validate_config(config, default):
    """
    Проверяет структуру конфига на соответствие стандартному шаблону.

    :param config: Текущий конфиг.
    :type config: `dict`

    :param default: Стандартный шаблон конфига.
    :type default: `dict`

    :return: True если структура валидна, иначе False.
    :rtype: bool
    """
    for key, value in default.items():
        if key not in config:
            return False
        if type(config[key]) is not type(value):
            return False
        if isinstance(value, dict) and isinstance(config[key], dict):
            if not validate_config(config[key], value):
                return False
    return True

def restore_config(config: dict, default: dict):
    """
    Восстанавливает недостающие параметры в конфиге из стандартного шаблона.
    И удаляет параметры из конфига, которых нету в стандартном шаблоне.

    :param config: Текущий конфиг.
    :type config: `dict`

    :param default: Стандартный шаблон конфига.
    :type default: `dict`

    :return: Восстановленный конфиг.
    :rtype: `dict`
    """
    config = copy.deepcopy(config)

    def check_default(config, default):
        for key, value in dict(default).items():
            if key not in config:
                config[key] = value
            elif type(value) is not type(config[key]):
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                check_default(config[key], value)
        return config

    config = check_default(config, default)
    return config
    
def get_json(path: str, default: dict, need_restore: bool = True) -> dict:
    """
    Получает данные файла настроек.
    Создаёт файл настроек, если его нет.
    Добавляет новые данные, если такие есть.

    :param path: Путь к json файлу.
    :type path: `str`

    :param default: Стандартный шаблон файла.
    :type default: `dict`

    :param need_restore: Нужно ли сделать проверку на целостность конфига.
    :type need_restore: `bool`
    """
    folder_path = os.path.dirname(path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if need_restore:
            new_config = restore_config(config, default)
            if config != new_config:
                config = new_config
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
    except:
        config = default
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    finally:
        return config
    
def set_json(path: str, new: dict):
    """
    Устанавливает новые данные в файл настроек.

    :param path: Путь к json файлу.
    :type path: `str`

    :param new: Новые данные.
    :type new: `dict`
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(new, f, indent=4, ensure_ascii=False)

def configure_json(name: str, params: dict, accent_color: AnsiFore, 
                   data: dict | None = None):
    """
    Начинает настройку файла настроек для пользователя.

    :param path: Путь к json файлу.
    :type path: `str`

    :param default: Стандартная структура файла.
    :type default: `dict`

    :param accent_color: Цвет акцента.
    :type accent_color: `colorama.Fore`

    :param params: Параметры, которые нужно настроить.
    :type params: `dict`
    """
    answers = {}
    config = Settings.get(name, data)

    def configure(params, default, config, prefix=""):
        for key, value in params.items():
            full_key = f"{accent_color}{prefix}{key}"
            if isinstance(value, dict) and "type" not in value:
                if key not in config:
                    config[key] = default[key]
                configure(value, default[key], config[key], prefix=full_key + f"{Fore.LIGHTWHITE_EX}.{accent_color}")
            else:
                full_key = full_key.replace(key, f"{Fore.LIGHTYELLOW_EX}{key}")
                not_stated_placeholder = "Не задано"
                default_value = default.get(key, "")
                desc = "· " + "\n· ".join(value.get("desc", []))
                while True:
                    print(f"\n{Fore.LIGHTWHITE_EX}⚙️ Введите значение параметра {full_key}{Fore.LIGHTWHITE_EX}."
                          f"\n{Fore.WHITE}Значение по умолчанию: {accent_color}{default_value if default_value else not_stated_placeholder}"
                          f"\n{Fore.WHITE}Описание параметра: \n{accent_color}{desc}"
                          f'\n{Fore.WHITE}Ввод {"обязательный" if value.get("required") else "необязательный"}')
                    if not value.get("required"):
                        print(f"{Fore.LIGHTWHITE_EX}Нажмите Enter, чтобы пропустить и использовать значение по умолчанию: {accent_color}{default_value if default_value else not_stated_placeholder}")
                    a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")

                    param_type = value.get("type")
                    if param_type is int:
                        if a:
                            try:
                                answers[key] = int(a)
                                config[key] = int(a)
                                print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{full_key} {Fore.WHITE}было изменено на {accent_color}{a}")
                                break
                            except ValueError:
                                print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть числовым. Попробуйте снова.")
                        elif value.get("required"):
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное. Попробуйте снова.")
                        else:
                            answers[key] = default_value
                            config[key] = default_value
                            print(f"Будет использоваться значение по умолчанию: {accent_color}{default_value if default_value else not_stated_placeholder}")
                            break
                    elif param_type is str:
                        if a:
                            answers[key] = str(a)
                            config[key] = str(a)
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{full_key} {Fore.WHITE}было изменено на {accent_color}{a}")
                            break
                        elif value.get("required"):
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное. Попробуйте снова.")
                        else:
                            answers[key] = default_value
                            config[key] = default_value
                            print(f"{Fore.WHITE}Будет использоваться значение по умолчанию: {accent_color}{default_value if default_value else not_stated_placeholder}")
                            break
        return config

    print(f"\n{Fore.LIGHTWHITE_EX}↓ Всего {accent_color}{len(params.keys())} {Fore.LIGHTWHITE_EX}раздела(-ов) для настройки.")
    new_config = configure(params, data[name]["default"], config)

    print(f"\n{Fore.LIGHTWHITE_EX}✓ Отлично, настройка была завершена."
          f"\n{Fore.WHITE}Ваши ответы:"
          f"\n{Fore.WHITE}Параметр: {accent_color}*ваш ответ*{Fore.WHITE} | {accent_color}*значение по умолчанию*")
    print(f"{Fore.LIGHTWHITE_EX}——————")
    for answer_param in answers.keys():
        print(f"{Fore.WHITE}{answer_param}: {accent_color}{answers[answer_param]}{Fore.WHITE}")

    print(f"\n{Fore.WHITE}💾 Применяем и сохраняем конфиг с текущими, указанными вами значениями? +/-")
    a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
    if a == "+":
        Settings.set(name, new_config, data)
        print(f"{Fore.LIGHTWHITE_EX}✅ Настройки были применены и сохранены в конфиг\n")
        return True
    else:
        print(f"\n{Fore.WHITE}Вы отказались от сохранения введённых вами значений в конфиг. Давайте настроим их с начала...")
        return configure_json(name, params, accent_color, data)

class Settings:

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

    @staticmethod
    def configure(name, accent_color, params: dict | None = None, 
                  data: dict | None = None) -> dict:
        data = data if data is not None else DATA
        if name not in data:
            return None
        return configure_json(name, params if params else data[name]["params"], accent_color, data)