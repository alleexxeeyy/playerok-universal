import importlib.resources
import os
import sys
import importlib
import pkg_resources
import uuid
from uuid import UUID
from pathlib import Path
import subprocess
from colorama import Fore, Style

from core.handlers_manager import HandlersManager

class ModuleMeta:
    """
    Класс, содержащий метаданные модуля.

    :param prefix: Префикс модуля.
    :type prefix: str

    :param version: Версия модуля.
    :type version: str

    :param name: Название модуля.
    :type name: str

    :param description: Описание модуля.
    :type description: str

    :param authors: Авторы модуля.
    :type authors: str

    :param links: Ссылки на авторов модуля.
    :type links: str
    """
    def __init__(self, prefix: str, version: str, name: str,
                 description: str, authors: str, links: str):
        self.prefix = prefix
        """ Префикс модуля. """
        self.version = version
        """ Версия модуля. """
        self.name = name
        """ Название модуля. """
        self.description = description
        """ Описание модуля. """
        self.authors = authors
        """ Авторы модуля. """
        self.links = links
        """ Ссылки на авторов модуля. """

class Module:
    """
    Объект модуля.

    :param uuid: UUID модуля (генерируется при инициализации).
    :type uuid: `UUID`

    :param enabled: Включен ли модуль.
    :type enabled: bool

    :param meta: Метаданные модуля.
    :type meta: `ModuleMeta`

    :param bot_event_handlers: Хендлеры ивентов бота.
    :type bot_event_handlers: dict

    :param playerok_event_handlers: Хендлеры ивентов Playerok.
    :type playerok_event_handlers: dict

    :param telegram_bot_routers: Роутеры Telegram бота.
    :type telegram_bot_routers: list[`Router`]

    :param _dir_name: Имя директории бота в папке модулей.
    :type _dir_name: str
    """
    def __init__(self, enabled: bool, meta: ModuleMeta, bot_event_handlers: dict, 
                 playerok_event_handlers: dict, telegram_bot_routers: list, _dir_name: str):
        self.uuid: UUID = uuid.uuid4()
        """ UUID модуля (генерируется при инициализации). """
        self.enabled: bool = enabled
        """ Включен ли модуль. """
        self.meta: ModuleMeta = meta
        """ Метаданные модуля. """
        self.bot_event_handlers: dict = bot_event_handlers
        """ Хендлеры ивентов бота. """
        self.playerok_event_handlers: dict = playerok_event_handlers
        """ Хендлеры ивентов Playerok. """
        self.telegram_bot_routers: list = telegram_bot_routers
        """ Роутеры Telegram бота. """
        self._dir_name: str = _dir_name
        """ Имя директории бота в папке модулей. """


_loaded_modules: list[Module] = []
""" Загруженные модули. """

class ModulesManager:
    """
    Класс, описывающий взаимодействие с модулями бота.
    """    
    @staticmethod
    def set_modules(data: list[Module]):
        global _loaded_modules
        _loaded_modules = data

    @staticmethod
    def get_modules() -> list[Module]:
        global _loaded_modules
        return _loaded_modules

    @staticmethod
    def get_module_by_uuid(module_uuid: UUID) -> Module:
        """ 
        Получает модуль по UUID.
        
        :param module_uuid: UUID модуля.
        :type module_uuid: UUID

        :return: Объект модуля.
        :rtype: `Module`
        """
        global _loaded_modules
        for module in _loaded_modules:
            if module.uuid == module_uuid:
                return module
        return None

    @staticmethod
    def enable_module(module_uuid: UUID) -> bool:
        """
        Включает модуль и добавляет его хендлеры.

        :param module_uuid: UUID модуля.
        :type module_uuid: UUID
        """
        global _loaded_modules
        try:
            module = ModulesManager.get_module_by_uuid(module_uuid)
            if not module:
                raise Exception("Модуль не найден в загруженных")
        
            HandlersManager.register_bot_event_handlers(module.bot_event_handlers)
            HandlersManager.register_playerok_event_handlers(module.playerok_event_handlers)
            i = _loaded_modules.index(module)
            module.enabled = True
            _loaded_modules[i] = module
            print(f"{Fore.WHITE}🔌 Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}подключен")
            return True
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module_uuid}: {Fore.WHITE}{e}")
            return False

    @staticmethod
    def disable_module(module_uuid: UUID) -> bool:
        """ 
        Полностью выключает модуль и удаляет его хендлеры.
        
        :param module_uuid: UUID модуля.
        :type module_uuid: UUID
        """
        global _loaded_modules
        try:
            module = ModulesManager.get_module_by_uuid(module_uuid)
            if not module:
                raise Exception("Модуль не найден в загруженных")
            
            HandlersManager.remove_handlers(module.bot_event_handlers, module.playerok_event_handlers)
            i = _loaded_modules.index(module)
            module.enabled = False
            _loaded_modules[i] = module
            print(f"{Fore.LIGHTRED_EX}🚫 Модуль {module.meta.name} отключен")
            return True
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Ошибка при отключении модуля {module_uuid}: {Fore.WHITE}{e}")
            return False

    @staticmethod
    def reload_module(module_uuid: str):
        """
        Перезагружает модуль (отгружает и импортирует снова).
        
        :param module_uuid: UUID модуля.
        :type module_uuid: UUID
        """
        try:
            module = ModulesManager.get_module_by_uuid(module_uuid)
            if not module:
                raise Exception("Модуль не найден в загруженных")
            
            if module._dir_name in sys.modules:
                del sys.modules[f"modules.{module._dir_name}"]
            mod = importlib.import_module(f"modules.{module._dir_name}")
            print(f"{Fore.WHITE}🔄  Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}был перезагружен")
            return mod
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Ошибка при перезагрузке модуля {module_uuid}: {Fore.WHITE}{e}")
            return False

    @staticmethod
    def load_modules() -> list[Module]:
        """ Загружает все модули из папки modules. """
        modules = []
        modules_path = "modules"
        os.makedirs(modules_path, exist_ok=True)

        def is_package_installed(requirement_string: str) -> bool:
            """ Проверяет, установлена ли библотека. """
            try:
                pkg_resources.require(requirement_string)
                return True
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                return False

        def install_requirements(requirements_path: str):
            """
            Устанавливает зависимости с файла requirements.txt,
            если они не установлены.

            :param requirements_path: Путь к файлу requirements.txt.
            :type requirements_path: str
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
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])

        for name in os.listdir(modules_path):
            bot_event_handlers = {}
            playerok_event_handlers = {}
            telegram_bot_routers = []
            
            module_path = os.path.join(modules_path, name)
            if os.path.isdir(module_path) and "__init__.py" in os.listdir(module_path):
                try:
                    install_requirements(os.path.join(module_path, "requirements.txt"))

                    module = importlib.import_module(f"modules.{name}")
                    if hasattr(module, "BOT_EVENT_HANDLERS"):
                        for key, funcs in module.BOT_EVENT_HANDLERS.items():
                            bot_event_handlers.setdefault(key, []).extend(funcs)
                    if hasattr(module, "PLAYEROK_EVENT_HANDLERS"):
                        for key, funcs in module.PLAYEROK_EVENT_HANDLERS.items():
                            playerok_event_handlers.setdefault(key, []).extend(funcs)
                    if hasattr(module, "TELEGRAM_BOT_ROUTERS"):
                        telegram_bot_routers.extend(module.TELEGRAM_BOT_ROUTERS)
                    
                    module_data = Module(
                        enabled=False,
                        meta=ModuleMeta(
                            module.PREFIX,
                            module.VERSION,
                            module.NAME,
                            module.DESCRIPTION,
                            module.AUTHORS,
                            module.LINKS
                        ),
                        bot_event_handlers=bot_event_handlers,
                        playerok_event_handlers=playerok_event_handlers,
                        telegram_bot_routers=telegram_bot_routers,
                        _dir_name=name
                    )
                    modules.append(module_data)
                except Exception as e:
                    print(f"{Fore.LIGHTRED_EX}Ошибка при загрузке модуля {name}: {Fore.WHITE}{e}")
        return modules

    @staticmethod
    def connect_modules(modules: list[Module]):
        """ Подключает (включает) переданные в массиве модули. """
        global _loaded_modules
        names = []
        for module in modules:
            try:
                HandlersManager.register_bot_event_handlers(module.bot_event_handlers)
                HandlersManager.register_playerok_event_handlers(module.playerok_event_handlers)
                i = _loaded_modules.index(module)
                module.enabled = True
                _loaded_modules[i] = module
                names.append(f"{Fore.LIGHTYELLOW_EX}{module.meta.name} {Fore.LIGHTWHITE_EX}{module.meta.version}")
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module.meta.name}: {Fore.WHITE}{e}")
                continue
        print(f'{Fore.WHITE}🔌 Подключено {Fore.LIGHTWHITE_EX}{len(modules)} модуля(-ей): {f"{Fore.WHITE}, ".join(names)}')