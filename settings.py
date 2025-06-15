import json
from colorama import Fore, Style

class Config:
    PATH = "bot_settings/config.json"
    
    @staticmethod
    def get() -> dict:
        """ Возвращает содержимое config.json в JSON формате. """
        try:
            with open(Config.PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                def_config = Config.default_config()
                for k, v in def_config.items():
                    if k not in config:
                        config[k] = v
        except:
            with open(Config.PATH, 'w', encoding='utf-8') as f:
                json.dump(Config.default_config(), f, indent=4, ensure_ascii=False)
            with open(Config.PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        finally:
            return config
    
    @staticmethod
    def set(new_data):
        """ Перезаписывает данные в config.json. """
        with open(Config.PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def default_config() -> dict:
        """ Возвращает стандартную структуру config.json. """
        return {
            "token": "",
            "user_agent": "",
            "tg_admin_id": 0,
            "tg_bot_token": "",
            "playerokapi_requests_timeout": 30,
            "playerokapi_listener_requests_delay": 2,
            "messages_watermark_enabled": True,
            "messages_watermark": "©️ 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
            "read_chat_before_sending_message_enabled": True,
            "first_message_enabled": True,
            "custom_commands_enabled": True,
            "auto_deliveries_enabled": True,
            "auto_raising_items_enabled": True,
            "auto_raising_items_priority_status": "DEFAULT"
        }
    
    @staticmethod
    def configure_config():
        """ Начинает настройку конфига. """
        params = {
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
            "playerokapi_timeout": {
                "required": False,
                "type": int,
                "desc": [
                    "Максимальное время таймаут на подключение к playerok.com. Если у вас плохой интернет - указывайте значение больше. Указывается в секундах."
                ]
            },
            "listener_requests_delay": {
                "required": False,
                "type": int,
                "desc": [
                    "Периодичность отправления запросов на playerok.com для получения ивентов. Не рекомендуем ставить ниже 2, ",
                    "в виду повышенного риска блокировки вашего IP адреса со стороны Playerok. Указывается в секундах."
                ]
            },
            "tg_admin_id": {
                "required": True,
                "type": int,
                "desc": [
                    "ID вашего Telegram аккаунта. Можно узнать у бота @myidbot. Только пользователь с этим ID сможет взаимодействовать с ботом."
                ]
            },
            "tg_bot_token": {
                "required": True,
                "type": str,
                "desc": [
                    "Токен Telegram бота. В TG боте можно будет настроить остальную часть функционала бота.",
                    "Чтобы получить токен, нужно создать бота у @BotFather. Пишите /newbot и начинаете настройку."
                ]
            }
        }

        config = Config.get()
        answers = {}
        print(f"\n{Fore.LIGHTWHITE_EX}↓ Всего {Fore.LIGHTYELLOW_EX}{len(params.keys())} {Fore.LIGHTWHITE_EX}параметра(-ов), ничего сложного ( ͡° ͜ʖ ͡°)")
        i=0
        for param in params.keys():
            if param in config:
                i+=1
                not_stated_placeholder = "Не задано"
                default_value = config[param]
                desc = "· " + "\n· ".join(params[param]["desc"])
                print(f"\n{Fore.LIGHTWHITE_EX}⚙️ {i}. Введите значение параметра {Fore.LIGHTYELLOW_EX}{param}."
                      f"\n{Fore.WHITE}Значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value if default_value else not_stated_placeholder}"
                      f"\n{Fore.WHITE}Описание параметра: \n{Fore.LIGHTYELLOW_EX}{desc}"
                      f'\n{Fore.WHITE}Ввод {"обязательный" if params[param]["required"] else "необязательный"}')
                if not params[param]["required"]:
                    print(f"{Fore.LIGHTWHITE_EX}Нажмите Enter, чтобы пропустить и использовать значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value if default_value else not_stated_placeholder}")
                a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
                
                if params[param]["type"] is int:
                    try:
                        if int(a) > 0:
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{param} {Fore.WHITE}было изменено на {Fore.LIGHTYELLOW_EX}{a}")
                            answers[param] = int(a)
                            continue
                        elif int(a) <= 0:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: слишком низкое значение")
                            break
                    except:
                        if not a and not params[param]["required"]:
                            answers[param] = default_value
                            print(f"Будет использоваться значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value if default_value else not_stated_placeholder}")
                        elif not a and params[param]["required"]:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное")
                            break
                        else:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть числовым")
                            break
                elif params[param]["type"] is str:
                    try:
                        if len(a) > 0:
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{param} {Fore.WHITE}было изменено на {Fore.LIGHTYELLOW_EX}{a}")
                            answers[param] = str(a)
                            continue
                        elif not a and params[param]["required"]:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное")
                            break
                        elif not a and not params[param]["required"]:
                            answers[param] = default_value
                            print(f"{Fore.WHITE}Будет использоваться значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value if default_value else not_stated_placeholder}")
                    except:
                        print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть строчным")
                        break
        else:
            print(f"\n{Fore.LIGHTWHITE_EX}✓ Отлично, настройка была завершена.")
            print(f"{Fore.WHITE}Ваши ответы:")
            print(f"{Fore.WHITE}Параметр: {Fore.LIGHTYELLOW_EX}*ваш ответ*{Fore.WHITE} | {Fore.LIGHTYELLOW_EX}*значение по умолчанию*")
            print(f"{Fore.LIGHTWHITE_EX}——————")
            for answer_param in answers.keys():
                default_value = config[answer_param]
                print(f"{Fore.WHITE}{answer_param}: {Fore.LIGHTYELLOW_EX}{answers[answer_param]}{Fore.WHITE} | {Fore.LIGHTYELLOW_EX}{default_value if default_value else not_stated_placeholder}")
            print(f"\n{Fore.WHITE}💾 Применяем и сохраняем конфиг с текущими, указанными вами значениями? +/-")
            a = input(f"{Fore.WHITE}> ")

            if a == "+":
                for answer_param in answers.keys():
                    config[answer_param] = answers[answer_param]
                    Config.set(config)
                print(f"{Fore.LIGHTWHITE_EX}✅ Настройки были применены и сохранены в конфиг\n")
                return True
            else:
                print(f"\n{Fore.WHITE}Вы отказались от сохранения введённых вами значений в конфиг. Давайте настроим их с начала...")
                return Config.configure_config()
        print(f"{Fore.WHITE}К сожалению, вы ввели неверное значение для одного из параметров, и поэтому настройка начнётся с самого начала")
        return Config.configure_config()
    
class Messages:
    PATH = "bot_settings/messages.json"

    @staticmethod
    def get() -> dict:
        """ Возвращает содержимое messages.json в JSON формате. """
        try:
            with open(Messages.PATH, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except:
            with open(Messages.PATH, 'w', encoding='utf-8') as f:
                json.dump(Messages.default_messages(), f, indent=4, ensure_ascii=False)
            with open(Messages.PATH, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        finally:
            return messages
        
    @staticmethod
    def set(new_data):
        """ Перезаписывает данные в messages.json. """
        with open(Messages.PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def default_messages() -> dict:
        """ Возвращает стандартную структуру messages.json. """
        return {
            "user_not_initialized": [
                "👋 Привет, {buyer_username}! Я бот-помощник 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                "",
                "🗨️ Если вы хотите поговорить с продавцом, напишите команду !продавец, чтобы я пригласил его в этот диалог.",
                "",
                "🕹️ А вообще, чтобы узнать все мои команды, напишите !команды"
            ], 
            "command_error": [
                "✗ При вводе команды произошла непредвиденная ошибка"
            ],
            "command_incorrect_use_error": [
                "✗ Неверное использование команды. Используйте {correct_use}"
            ],
            "buyer_command_commands": [
                "🕹️ Основные команды:",
                "→ !продавец — уведомить и позвать продавца в этот чат"
            ],
            "buyer_command_seller": [
                "💬 Продавец был вызван в этот чат. Ожидайте, пока он подключиться к диалогу..."
            ],
            "deal_confirmed": [
                "🌟 Спасибо за успешную сделку. Буду рад, если оставите отзыв. Жду вас в своём магазине в следующий раз, удачи!"
            ]
        }

class CustomCommands:
    PATH = "bot_settings/custom_commands.json"
    
    @staticmethod
    def get() -> dict:
        """ Возвращает содержимое custom_commands.json в JSON формате. """
        try:
            with open(CustomCommands.PATH, 'r', encoding='utf-8') as f:
                custom_commands = json.load(f)
        except:
            with open(CustomCommands.PATH, 'w', encoding='utf-8') as f:
                json.dump(CustomCommands.default_custom_commands(), f, indent=4, ensure_ascii=False)
            with open(CustomCommands.PATH, 'r', encoding='utf-8') as f:
                custom_commands = json.load(f)
        finally:
            return custom_commands
        
    @staticmethod
    def set(new_data):
        """ Перезаписывает данные в custom_commands.json. """
        with open(CustomCommands.PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def default_custom_commands() -> dict:
        """ Возвращает стандартную структуру custom_commands.json. """
        return {
            "!тест": [
                "Привет, друг 👋. Это тестовое сообщение, которое можно изменить в настройках пользовательских команд.",
                "©️ 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
            ]
        }

class AutoDeliveries:
    PATH = "bot_settings/auto_deliveries.json"
    
    @staticmethod
    def get() -> dict:
        """ Возвращает содержимое auto_deliveries.json в JSON формате. """
        try:
            with open(AutoDeliveries.PATH, 'r', encoding='utf-8') as f:
                auto_deliveries = json.load(f)
        except:
            with open(AutoDeliveries.PATH, 'w', encoding='utf-8') as f:
                json.dump(AutoDeliveries.default_auto_deliveries(), f, indent=4, ensure_ascii=False)
            with open(AutoDeliveries.PATH, 'r', encoding='utf-8') as f:
                auto_deliveries = json.load(f)
        finally:
            return auto_deliveries
        
    @staticmethod
    def set(new_data):
        """ Перезаписывает данные в auto_deliveries.json """
        with open(AutoDeliveries.PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        
    @staticmethod
    def default_auto_deliveries() -> dict:
        """ Возвращает стандартную структуру auto_deliveries.json. """
        return {
            "xxxxxxxx-xxxxxxxxx-xxxxxxxxxx-xxxxxxxxx": [
                "Вот ваш аккаунт:",
                "- Логин: login123",
                "- Пароль: password123",
                "©️ 𝐅𝐮𝐧𝐏𝐚𝐲 𝐔𝐧𝐢𝐯𝐞𝐫𝐬𝐚𝐥"
            ]
        }