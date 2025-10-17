from dataclasses import dataclass
import os
import sys
import importlib
import uuid
from uuid import UUID
from colorama import Fore
from logging import getLogger
logger = getLogger(f"universal.modules")

from core.handlers import register_bot_event_handlers, register_playerok_event_handlers, remove_handlers
from core.utils import install_requirements


@dataclass
class ModuleMeta:
    prefix: str
    version: str
    name: str
    description: str
    authors: str
    links: str

@dataclass
class Module:
    uuid: UUID
    enabled: bool
    meta: ModuleMeta
    bot_event_handlers: dict
    playerok_event_handlers: dict
    telegram_bot_routers: list
    _dir_name: str


_loaded_modules: list[Module] = []

    
def set_modules(data: list[Module]):
    """
    Устанавливает новые модули в загруженные.

    :param data: Массив модулей.
    :type data: `list[core.modules.Module]`
    """
    global _loaded_modules
    _loaded_modules = data


def get_modules() -> list[Module]:
    """
    Возвращает загруженные модули.

    :return: Массив модулей.
    :rtype: `list[core.modules.Module]`
    """
    return _loaded_modules


def get_module_by_uuid(module_uuid: UUID) -> Module:
    """ 
    Получает модуль по UUID.
    
    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: Объект модуля.
    :rtype: `core.modules.Module`
    """
    try: return [module for module in _loaded_modules if module.uuid == module_uuid][0]
    except: return None


def enable_module(module_uuid: UUID) -> bool:
    """
    Включает модуль и добавляет его хендлеры.

    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: True, если модуль был включен. False, если не был включен.
    :rtype: `bool`
    """
    global _loaded_modules
    try:
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("Модуль не найден в загруженных")
        register_bot_event_handlers(module.bot_event_handlers)
        register_playerok_event_handlers(module.playerok_event_handlers)
        i = _loaded_modules.index(module)
        module.enabled = True
        _loaded_modules[i] = module
        logger.info(f"Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}подключен")

        def handle_on_module_enabled():
            """ 
            Запускается при включении модуля.
            Запускает за собой все хендлеры ON_MODULE_ENABLED.
            """
            for handler in module.bot_event_handlers.get("ON_MODULE_ENABLED", []):
                try:
                    handler(module)
                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_MODULE_ENABLED: {Fore.WHITE}{e}")
        handle_on_module_enabled()
        return True
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


def disable_module(module_uuid: UUID) -> bool:
    """ 
    Выключает модуль и удаляет его хендлеры.
    
    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: True, если модуль был выключен. False, если не был выключен.
    :rtype: `bool`
    """
    global _loaded_modules
    try:
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("Модуль не найден в загруженных")
        remove_handlers(module.bot_event_handlers, module.playerok_event_handlers)
        i = _loaded_modules.index(module)
        module.enabled = False
        _loaded_modules[i] = module
        logger.info(f"Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}отключен")
        
        def handle_on_module_disabled():
            """ 
            Запускается при выключении модуля.
            Запускает за собой все хендлеры ON_MODULE_DISABLED.
            """
            for handler in module.bot_event_handlers.get("ON_MODULE_DISABLED", []):
                try:
                    handler(module)
                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_MODULE_DISABLED: {Fore.WHITE}{e}")
        handle_on_module_disabled()
        return True
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при отключении модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


def reload_module(module_uuid: str):
    """
    Перезагружает модуль (отгружает и импортирует снова).
    
    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: True, если модуль был перезагружен. False, если не был перезагружен.
    :rtype: `bool`
    """
    try:
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("Модуль не найден в загруженных")
        if module._dir_name in sys.modules:
            del sys.modules[f"modules.{module._dir_name}"]
        mod = importlib.import_module(f"modules.{module._dir_name}")
        logger.info(f"Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}перезагружен")

        def handle_on_module_reloaded():
            """ 
            Запускается при первом подключении модуля.
            Запускает за собой все хендлеры ON_MODULE_RELOADED.
            """
            for handler in module.bot_event_handlers.get("ON_MODULE_RELOADED", []):
                try:
                    handler(module)
                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_MODULE_RELOADED: {Fore.WHITE}{e}")
        handle_on_module_reloaded()
        return mod
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при перезагрузке модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


def load_modules() -> list[Module]:
    """
    Загружает все модули из папки modules.
    
    :return: Массив загруженных модулей.
    :rtype: `list[core.modules.Module]`
    """
    modules = []
    modules_path = "modules"
    os.makedirs(modules_path, exist_ok=True)
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
                    uuid.uuid4(),
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
                logger.error(f"{Fore.LIGHTRED_EX}Ошибка при загрузке модуля {name}: {Fore.WHITE}{e}")
    return modules


def connect_modules(modules: list[Module]):
    """
    Подключает переданные модули (при запуске бота).

    :param modules: Массив модулей.
    :type modules: `list[core.modules.Module]`
    """
    global _loaded_modules
    names = []
    for module in modules:
        try:
            register_bot_event_handlers(module.bot_event_handlers)
            register_playerok_event_handlers(module.playerok_event_handlers)
            i = _loaded_modules.index(module)
            module.enabled = True
            _loaded_modules[i] = module
            names.append(f"{Fore.YELLOW}{module.meta.name} {Fore.LIGHTWHITE_EX}{module.meta.version}")
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module.meta.name}: {Fore.WHITE}{e}")
            continue
    logger.info(f'{Fore.LIGHTBLUE_EX}Подключено {Fore.CYAN}{len(modules)} модуля(-ей): {f"{Fore.WHITE}, ".join(names)}')
    
    def on_module_connected():
        """
        Запускается при первом подключении модуля. 
        Запускает за собой все хендлеры ON_MODULE_CONNECTED.
        """
        for module in modules:
            for handler in module.bot_event_handlers.get("ON_MODULE_CONNECTED", []):
                try:
                    handler(module)
                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_MODULE_CONNECTED: {Fore.WHITE}{e}")
    if module.enabled:
        on_module_connected()