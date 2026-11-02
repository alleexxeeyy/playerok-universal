import os
import re
import sys
import html
import stat
import shutil
import zipfile
import rarfile
import importlib
import traceback
import uuid
from uuid import UUID
from colorama import Fore
from dataclasses import dataclass
from logging import getLogger

from __init__ import ACCENT_COLOR
from core.handlers import (
    register_bot_event_handlers,
    register_playerok_event_handlers,
    remove_bot_event_handlers,
    remove_playerok_event_handlers,
    call_bot_event
)
from core.configs import TEMP_DIR
from core.utils import install_requirements


logger = getLogger("universal.modules")

MODULES_DIR = "modules"
MODULES_TEMP_DIR = os.path.join(TEMP_DIR, "modules")
MODULE_EXTENSIONS = (".zip", ".rar")
MAX_MODULE_SIZE = 50 * 1024 * 1024
MAX_UNPACKED_SIZE = 300 * 1024 * 1024
MAX_NESTING = 5

JUNK_NAMES = {"__MACOSX", "__pycache__", ".git", ".idea", ".vscode", ".DS_Store", "Thumbs.db"}
_RAR_TOOL_ERRORS = tuple(e for e in (getattr(rarfile, "RarCannotExec", None),) if e)


class ModuleImportError(Exception):
    """Ошибка импорта модуля с готовым к отправке пользователю текстом."""


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


loaded_modules: list[Module] = []


def get_modules():
    """
    Возвращает загруженные модули.

    :return: Загруженные модули
    :rtype: `list` of `core.modules.Module`
    """
    return loaded_modules


def set_modules(modules: list[Module]):
    """
    Устанавливает загруженные модули.

    :param modules: Новые загруженные модули
    :type modules: `list` of `core.modules.Module`
    """
    global loaded_modules
    loaded_modules = modules


def get_module_by_uuid(module_uuid: UUID) -> Module | None:
    """ 
    Получает модуль по UUID.
    
    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: Объект модуля.
    :rtype: `core.modules.Module` or `None`
    """
    try: return [module for module in loaded_modules if module.uuid == module_uuid][0]
    except: return None


async def _enable_module(module: Module) -> bool:
    global loaded_modules

    register_bot_event_handlers(module.bot_event_handlers)
    register_playerok_event_handlers(module.playerok_event_handlers)

    module.enabled = True
    loaded_modules[loaded_modules.index(module)] = module

    handlers = module.bot_event_handlers.get("ON_MODULE_ENABLED", [])
    for handler in handlers:
        await call_bot_event("ON_MODULE_ENABLED", [module], handler)


async def enable_module(module_uuid: UUID) -> bool:
    """
    Включает модуль и добавляет его хендлеры.

    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: True, если модуль был включен. False, если не был включен.
    :rtype: `bool`
    """
    try:
        module = get_module_by_uuid(module_uuid)
    
        await _enable_module(module)
        logger.info(f"Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}включен")
        
        return True
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при включении модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


async def _disable_module(module: Module) -> bool:
    global loaded_modules
        
    remove_bot_event_handlers(module.bot_event_handlers)
    remove_playerok_event_handlers(module.playerok_event_handlers)

    module.enabled = False
    loaded_modules[loaded_modules.index(module)] = module

    handlers = module.bot_event_handlers.get("ON_MODULE_DISABLED", [])
    for handler in handlers:
        await call_bot_event("ON_MODULE_DISABLED", [module], handler)


async def disable_module(module_uuid: UUID) -> bool:
    """ 
    Выключает модуль и удаляет его хендлеры.
    
    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: True, если модуль был выключен. False, если не был выключен.
    :rtype: `bool`
    """
    try:
        module = get_module_by_uuid(module_uuid)
    
        await _disable_module(module)
        logger.info(f"Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}выключен")
        
        return True
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при выключении модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


async def reload_module(module_uuid: str):
    """
    Перезагружает модуль (отгружает и импортирует снова).
    
    :param module_uuid: UUID модуля.
    :type module_uuid: `uuid.UUID`

    :return: True, если модуль был перезагружен. False, если не был перезагружен.
    :rtype: `bool`
    """
    try:
        module = get_module_by_uuid(module_uuid)
        
        await _disable_module(module)
        if module._dir_name in sys.modules:
            del sys.modules[f"{MODULES_DIR}.{module._dir_name}"]
        importlib.import_module(f"{MODULES_DIR}.{module._dir_name}")
        await _enable_module(module)

        logger.info(f"Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}перезагружен")
        return True
    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при перезагрузке модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


IGNORED_NAMES = {"__pycache__", "__init__.py"}


def _import_module_object(stem: str) -> Module:
    module = importlib.import_module(f"{MODULES_DIR}.{stem}")
    return Module(
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
        bot_event_handlers=getattr(module, "BOT_EVENT_HANDLERS", None) or {},
        playerok_event_handlers=getattr(module, "PLAYEROK_EVENT_HANDLERS", None) or {},
        telegram_bot_routers=getattr(module, "TELEGRAM_BOT_ROUTERS", None) or [],
        _dir_name=stem
    )


def load_modules() -> list[Module]:
    """Загружает все модули из папки modules (папки с __init__.py и одиночные .py файлы)."""
    global loaded_modules

    modules = []
    seen_stems = set()
    os.makedirs(MODULES_DIR, exist_ok=True)

    # папки-модули грузим первыми: при коллизии имени (foo/ и foo.py) Python
    # всё равно импортирует пакет, поэтому за ним и закрепляем stem
    names = sorted(os.listdir(MODULES_DIR), key=lambda n: not os.path.isdir(os.path.join(MODULES_DIR, n)))
    for name in names:
        if name in IGNORED_NAMES or name.startswith("pyarmor_runtime_"):
            continue
        module_path = os.path.join(MODULES_DIR, name)

        if os.path.isdir(module_path) and "__init__.py" in os.listdir(module_path):
            stem = name
            requirements = os.path.join(module_path, "requirements.txt")
        elif os.path.isfile(module_path) and name.endswith(".py"):
            stem = name[:-3]
            requirements = os.path.join(MODULES_DIR, stem, "requirements.txt")
        else:
            continue

        if stem in seen_stems:
            logger.warning(
                f"{Fore.LIGHTYELLOW_EX}Пропускаю {name}: модуль с именем "
                f"{Fore.LIGHTWHITE_EX}{stem} {Fore.LIGHTYELLOW_EX}уже загружен"
            )
            continue

        try:
            if os.path.isfile(requirements):
                install_requirements(requirements)
            modules.append(_import_module_object(stem))
            seen_stems.add(stem)
        except:
            logger.error(
                f"{Fore.LIGHTRED_EX}Ошибка при загрузке модуля {name}: "
                f"{Fore.WHITE}{traceback.format_exc()}"
            )

    return modules


def _grant_write(path: str):
    try:
        os.chmod(path, os.stat(path).st_mode | stat.S_IRWXU)
    except Exception:
        pass


def _rm_error(func, path, exc):
    _grant_write(os.path.dirname(path))
    _grant_write(path)
    try:
        func(path)
    except Exception:
        pass


def _rmtree(path: str):
    if not os.path.exists(path):
        return
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_rm_error)
    else:
        shutil.rmtree(path, onerror=_rm_error)


def _open_archive(path: str):
    if path.lower().endswith(".zip"):
        primary, fallback = zipfile.ZipFile, rarfile.RarFile
    else:
        primary, fallback = rarfile.RarFile, zipfile.ZipFile

    try:
        return primary(path)
    except Exception as e:
        primary_error = e

    try:
        return fallback(path)
    except Exception:
        pass

    if isinstance(primary_error, _RAR_TOOL_ERRORS):
        raise ModuleImportError(
            "❌ Не удалось открыть RAR — на устройстве нет утилиты <b>unrar</b>. "
            "Пришлите модуль архивом <b>.zip</b>"
        )
    raise ModuleImportError("❌ Не удалось открыть архив — файл битый или это не архив")


def _member_parts(name: str) -> list[str] | None:
    name = (name or "").replace("\\", "/")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        return None

    parts = [p for p in name.split("/") if p and p != "."]
    if not parts or any(p == ".." for p in parts):
        return None
    if any(p in JUNK_NAMES or p.startswith("._") for p in parts):
        return None
    return parts


def _extract_archive(path: str, dest: str):
    with _open_archive(path) as archive:
        try:
            infos = archive.infolist()
        except Exception:
            raise ModuleImportError("❌ Не удалось прочитать архив — файл битый или защищён паролем")

        total = 0
        files = 0

        for info in infos:
            try:
                is_dir = info.is_dir()
            except Exception:
                is_dir = str(getattr(info, "filename", "")).endswith("/")
            if is_dir:
                continue

            parts = _member_parts(getattr(info, "filename", ""))
            if not parts:
                continue

            target = os.path.join(dest, *parts)
            try:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with archive.open(info) as src, open(target, "wb") as out:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > MAX_UNPACKED_SIZE:
                            raise ModuleImportError(
                                f"❌ Содержимое архива слишком большое "
                                f"(максимум {MAX_UNPACKED_SIZE // 1024 // 1024} МБ в распакованном виде)"
                            )
                        out.write(chunk)
            except ModuleImportError:
                raise
            except Exception as e:
                if isinstance(e, _RAR_TOOL_ERRORS):
                    raise ModuleImportError(
                        "❌ Не удалось распаковать RAR — на устройстве нет утилиты <b>unrar</b>. "
                        "Пришлите модуль архивом <b>.zip</b>"
                    )
                raise ModuleImportError(
                    f"❌ Не удалось распаковать архив: <blockquote>{html.escape(str(e))}</blockquote>"
                )
            files += 1

        if not files:
            raise ModuleImportError("❌ В архиве нет файлов")


def _find_module_roots(path: str, depth: int = 0) -> list[str]:
    if os.path.isfile(os.path.join(path, "__init__.py")):
        return [path]

    dirs = sorted(
        os.path.join(path, name) for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    )
    roots = [d for d in dirs if os.path.isfile(os.path.join(d, "__init__.py"))]

    if not roots and len(dirs) == 1 and depth < MAX_NESTING:
        return _find_module_roots(dirs[0], depth + 1)
    return roots


def _safe_module_name(source: str) -> str:
    name = os.path.splitext(os.path.basename(source.replace("\\", "/").rstrip("/")))[0]
    name = re.sub(r"[^0-9A-Za-z_]+", "_", name).strip("_")

    stripped = re.sub(r"_[vV]?\d+(?:_\d+)+$", "", name)
    if stripped:
        name = stripped

    if not name:
        return f"module_{uuid.uuid4().hex[:8]}"
    if name[0].isdigit():
        return f"module_{name}"
    return name


def prepare_module_import_dir(user_id: int | str) -> str:
    """
    Готовит чистую папку под присланный пользователем архив с модулем.

    :param user_id: ID пользователя Telegram, который прислал архив.
    :type user_id: `int` or `str`

    :return: Путь к папке.
    :rtype: `str`
    """
    path = os.path.join(MODULES_TEMP_DIR, str(user_id))
    _rmtree(path)
    os.makedirs(path, exist_ok=True)
    return path


def clear_module_import_dir(user_id: int | str):
    """
    Удаляет папку с присланным пользователем архивом.

    :param user_id: ID пользователя Telegram, который прислал архив.
    :type user_id: `int` or `str`
    """
    _rmtree(os.path.join(MODULES_TEMP_DIR, str(user_id)))


MODULE_DATA_DIRS = ("module_data", "module_settings")


def module_name_exists(name: str) -> bool:
    return os.path.isdir(os.path.join(MODULES_DIR, name)) or os.path.isfile(os.path.join(MODULES_DIR, f"{name}.py"))


def _free_module_name(base: str) -> str:
    n = 2
    while True:
        candidate = f"{base}_{n}"
        if not module_name_exists(candidate):
            return candidate
        n += 1


def _remove_stray_py(name: str):
    stray_py = os.path.join(MODULES_DIR, f"{name}.py")
    if os.path.isfile(stray_py):
        try:
            os.remove(stray_py)
        except Exception:
            raise ModuleImportError(
                f"❌ Не удалось заменить старую версию модуля <b>{name}</b> — файл занят или нет прав на запись"
            )


def stage_archive_modules(path: str, stage: str) -> list[dict]:
    if not path.lower().endswith(MODULE_EXTENSIONS):
        raise ModuleImportError("❌ Нужен архив в формате <b>.zip</b> или <b>.rar</b>")

    os.makedirs(MODULES_DIR, exist_ok=True)
    _rmtree(stage)
    os.makedirs(stage, exist_ok=True)

    _extract_archive(path, stage)

    roots = _find_module_roots(stage)
    if not roots:
        raise ModuleImportError(
            "❌ В архиве не найден модуль — внутри должна быть папка с файлом <code>__init__.py</code>"
        )

    found = []
    used = set()
    for root in roots:
        base = _safe_module_name(path if root == stage else root)
        name, n = base, 2
        while name in used:
            name = f"{base}_{n}"
            n += 1
        used.add(name)
        found.append({"name": name, "source": root, "is_py": False, "exists": module_name_exists(name)})
    return found


def stage_single_py_module(path: str, stage: str) -> list[dict]:
    if not path.lower().endswith(".py"):
        raise ModuleImportError("❌ Нужен файл в формате <b>.py</b>")

    os.makedirs(MODULES_DIR, exist_ok=True)
    _rmtree(stage)
    os.makedirs(stage, exist_ok=True)

    name = _safe_module_name(path)
    dst = os.path.join(stage, f"{name}.py")
    shutil.move(path, dst)
    return [{"name": name, "source": dst, "is_py": True, "exists": module_name_exists(name)}]


def _place_folder_replace(source: str, name: str) -> str:
    dest = os.path.join(MODULES_DIR, name)
    _remove_stray_py(name)
    if not os.path.exists(dest):
        shutil.move(source, dest)
        return name

    backup = os.path.join(MODULES_DIR, f".{name}.bak_import")
    _rmtree(backup)
    os.rename(dest, backup)
    try:
        shutil.move(source, dest)
    except Exception:
        _rmtree(dest)
        os.rename(backup, dest)
        raise ModuleImportError(
            f"❌ Не удалось заменить модуль <b>{name}</b> — старая версия восстановлена"
        )
    _rmtree(backup)
    return name


def _place_folder_merge(source: str, name: str) -> str:
    dest = os.path.join(MODULES_DIR, name)
    _remove_stray_py(name)
    os.makedirs(dest, exist_ok=True)
    try:
        for root, _, files in os.walk(source):
            for file in files:
                src_file = os.path.join(root, file)
                rel = os.path.relpath(src_file, source)
                if rel.replace("\\", "/").split("/")[0] in MODULE_DATA_DIRS:
                    continue
                dst_file = os.path.join(dest, rel)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
    except Exception:
        raise ModuleImportError(
            f"❌ Не удалось обновить модуль <b>{name}</b> — файл занят или нет прав на запись"
        )
    return name


def _place_py(source: str, name: str, wipe_folder: bool) -> str:
    dest = os.path.join(MODULES_DIR, f"{name}.py")
    if wipe_folder:
        _rmtree(os.path.join(MODULES_DIR, name))
    if os.path.isfile(dest):
        try:
            os.remove(dest)
        except Exception:
            raise ModuleImportError(
                f"❌ Не удалось заменить старую версию модуля <b>{name}</b> — файл занят или нет прав на запись"
            )
    shutil.move(source, dest)
    return name


def install_staged_module(mod: dict, action: str) -> str:
    name, source, is_py = mod["name"], mod["source"], mod["is_py"]

    if action == "duplicate":
        name = _free_module_name(name)
        return _place_py(source, name, True) if is_py else _place_folder_replace(source, name)

    if is_py:
        return _place_py(source, name, action != "merge")

    if action == "merge":
        return _place_folder_merge(source, name)
    return _place_folder_replace(source, name)


def _format_string(count: int):
    last_num = int(str(count)[-1])
    if last_num == 1: 
        return f"Подключен {Fore.LIGHTWHITE_EX}{count} модуль"
    elif 2 <= last_num <= 4: 
        return f"Подключено {Fore.LIGHTWHITE_EX}{count} модуля"
    elif 5 <= last_num <= 9 or last_num == 0: 
        return f"Подключено {Fore.LIGHTWHITE_EX}{count} модулей"


async def connect_modules(modules: list[Module]):
    """
    Подключает загруженные модули.
    
    :param modules: Загруженные модули
    :type modules: `list` of `core.modules.Module`
    """
    global loaded_modules

    for module in modules:
        try:
            await _enable_module(module)
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module.meta.name}: {Fore.WHITE}{traceback.format_exc()}")
    
    connected_modules = [module for module in loaded_modules if module.enabled]
    names = [f"{Fore.YELLOW}{module.meta.name} {Fore.LIGHTWHITE_EX}{module.meta.version}" for module in connected_modules]
    if names:
        logger.info(f'{_format_string(len(connected_modules))}{Fore.WHITE}: {f"{Fore.WHITE}, ".join(names)}')