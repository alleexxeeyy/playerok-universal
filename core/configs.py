import os
import re
import json
import time
import shutil
import zipfile
import rarfile
from datetime import datetime
from logging import getLogger

from settings import DATA, SettingsFile, Settings as sett, restore_config, set_json
from data import DATA as DATA_FILES, DataFile, Data as bot_data


logger = getLogger("universal.configs")

TEMP_DIR = "temp"
CONFIGS_TEMP_DIR = os.path.join(TEMP_DIR, "configs")
BACKUPS_DIR = "bot_settings/backups"
BACKUP_PREFIX = "backup_"
BACKUP_COOLDOWN = 60
MAX_BACKUPS = 5
MAX_IMPORT_SIZE = 10 * 1024 * 1024
MAX_MEMBER_SIZE = 5 * 1024 * 1024
EXPORT_ALL_NAME = "Конфиг Playerok Universal.zip"
EXPORT_FULL_NAME = "Конфиг и данные Playerok Universal.zip"
SUPPORTED_EXTENSIONS = (".json", ".zip", ".rar")

SECRET_PATHS = [
    ("playerok", "api", "cookies"),
    ("playerok", "api", "user_agent"),
    ("playerok", "api", "proxy"),
    ("telegram", "api", "token"),
    ("telegram", "api", "proxy"),
    ("telegram", "api", "custom_api_url"),
    ("telegram", "bot", "password")
]
KEEP_ALWAYS = [
    ("telegram", "bot", "signed_users")
]


def _all_files(with_data: bool = True) -> list[SettingsFile | DataFile]:
    return list(DATA) + (list(DATA_FILES) if with_data else [])


def _is_data(file: SettingsFile | DataFile) -> bool:
    return isinstance(file, DataFile)


def _read_file(file: SettingsFile | DataFile):
    return bot_data.get(file.name) if _is_data(file) else sett.get(file.name)


def _write_file(file: SettingsFile | DataFile, new: dict | list):
    # пишем через set_json, а не через Settings.set / Data.set: те глотают исключения,
    # и импорт отчитался бы «применено» там, где файл на диск не лёг
    os.makedirs(os.path.dirname(file.path), exist_ok=True)
    set_json(file.path, new)


def _file_by_name(name: str, with_data: bool = True) -> SettingsFile | DataFile | None:
    try: return [file for file in _all_files(with_data) if file.name == name][0]
    except: return None


def _file_by_json_name(json_name: str, with_data: bool = True) -> SettingsFile | DataFile | None:
    try:
        return [
            file for file in _all_files(with_data)
            if os.path.basename(file.path).lower() == json_name.lower()
        ][0]
    except: return None


def _get_by_path(data: dict, path: tuple):
    current = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None, False
        current = current[key]
    return current, True


def _set_by_path(data: dict, path: tuple, value):
    current = data
    for key in path[:-1]:
        if not isinstance(current.get(key), dict):
            current[key] = {}
        current = current[key]
    current[path[-1]] = value


def _open_archive(path: str):
    try:
        if path.lower().endswith(".zip"):
            return zipfile.ZipFile(path)
        return rarfile.RarFile(path)
    except Exception:
        # сырое исключение библиотеки тащит в текст путь к файлу, отдаём своё
        raise Exception("❌ Не удалось открыть архив — файл битый или это не архив")


def _archive_members(archive) -> list[tuple[str, int]]:
    members = []
    for info in archive.infolist():
        if info.is_dir() or not os.path.basename(info.filename):
            continue
        members.append((info.filename, info.file_size or 0))
    return members


def _read_member(archive, name: str) -> bytes:
    # заявленному размеру из заголовка архива не доверяем: читаем потоком
    # и обрываемся на лимите, иначе распаковка может съесть память
    with archive.open(name) as f:
        raw = f.read(MAX_MEMBER_SIZE + 1)

    if len(raw) > MAX_MEMBER_SIZE:
        raise Exception(f"слишком большой (максимум {MAX_MEMBER_SIZE // 1024 // 1024} МБ)")
    return raw


def _user_dir(user_id: int | str, name: str) -> str:
    return os.path.join(CONFIGS_TEMP_DIR, str(user_id), name)


def safe_file_name(name: str) -> str:
    """
    Чистит имя присланного файла, чтобы оно не ломало разметку сообщений
    и не уводило запись за пределы папки импорта.

    :param name: Имя файла.
    :type name: `str`

    :return: Очищенное имя файла.
    :rtype: `str`
    """
    name = os.path.basename((name or "").replace("\\", "/"))
    name = re.sub(r"[^\w\s.\-()]", "_", name, flags=re.UNICODE).strip(" .")
    return name or "file"


def _prepare_dir(path: str) -> str:
    _clear_dir(path)
    os.makedirs(path, exist_ok=True)
    return path


def _clear_dir(path: str):
    try: shutil.rmtree(path)
    except: pass
    _prune_empty_dirs(os.path.dirname(path))


def _prune_empty_dirs(path: str):
    """Убирает опустевшие папки внутри temp, чтобы она не висела после выгрузки."""
    root = os.path.abspath(TEMP_DIR)
    current = os.path.abspath(path)

    while current == root or current.startswith(root + os.sep):
        try:
            if os.listdir(current):
                return
            os.rmdir(current)
        except: return

        if current == root:
            return
        current = os.path.dirname(current)


def clear_temp_dir():
    """Убирает из temp опустевшие папки и саму temp, если в ней ничего не осталось."""
    # снизу вверх, иначе пустая вложенная папка (например после падения на распаковке)
    # так и держала бы temp на диске
    for current, _, _ in os.walk(TEMP_DIR, topdown=False):
        if os.path.abspath(current) == os.path.abspath(TEMP_DIR):
            continue
        try:
            if not os.listdir(current):
                os.rmdir(current)
        except: pass

    _prune_empty_dirs(TEMP_DIR)


def export_all(user_id: int | str, with_data: bool = False) -> str:
    """
    Выгружает все конфиги бота в архив.

    :param user_id: ID пользователя Telegram, который запросил выгрузку.
    :type user_id: `int` or `str`

    :param with_data: Добавить в архив файлы данных бота (bot_data).
    :type with_data: `bool`

    :return: Путь к архиву.
    :rtype: `str`
    """
    path = os.path.join(
        _prepare_dir(_user_dir(user_id, "export")),
        EXPORT_FULL_NAME if with_data else EXPORT_ALL_NAME
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in _all_files(with_data):
            data = _read_file(file)
            if data is None:
                continue
            archive.writestr(
                file.path,
                json.dumps(data, ensure_ascii=False, indent=4)
            )
    return path


def export_file(user_id: int | str, name: str = "config") -> str:
    """
    Выгружает один конфиг бота в файл.

    :param user_id: ID пользователя Telegram, который запросил выгрузку.
    :type user_id: `int` or `str`

    :param name: Название конфига.
    :type name: `str`

    :return: Путь к файлу.
    :rtype: `str`
    """
    file = _file_by_name(name)
    if not file:
        raise Exception(f"❌ Конфиг {name} не найден")

    data = _read_file(file)
    if data is None:
        raise Exception(f"❌ Не удалось прочитать конфиг {os.path.basename(file.path)}")

    path = os.path.join(
        _prepare_dir(_user_dir(user_id, "export")),
        os.path.basename(file.path)
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return path


def clear_export_dir(user_id: int | str):
    """Удаляет папку с выгруженными конфигами пользователя."""
    _clear_dir(_user_dir(user_id, "export"))


def _rotate_backups():
    try:
        for name in list_backups()[MAX_BACKUPS:]:
            try: os.remove(os.path.join(BACKUPS_DIR, name))
            except: pass
    except Exception as e:
        logger.debug(f"Не удалось почистить старые бэкапы конфигов: {e}")


def _backup_path() -> str:
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"{BACKUP_PREFIX}{now}"

    try: existing = os.listdir(BACKUPS_DIR)
    except: existing = []

    # счётчик берём монотонным (max + 1), а не первым свободным именем:
    # ротация освобождает самое старое имя, и первый свободный бэкап занял бы его снова,
    # после чего был бы удалён следующей же ротацией
    counter = 0
    for name in existing:
        if not name.startswith(prefix) or not name.lower().endswith(".zip"):
            continue

        tail = name[len(prefix):-len(".zip")]
        if not tail:
            counter = max(counter, 1)
        elif tail.startswith("_") and tail[1:].isdigit():
            counter = max(counter, int(tail[1:]))

    if not counter:
        return os.path.join(BACKUPS_DIR, f"{prefix}.zip")
    # счётчик паддим, иначе сортировка по имени поставит _2 выше _10
    return os.path.join(BACKUPS_DIR, f"{prefix}_{counter + 1:02d}.zip")


def make_backup() -> str | None:
    """
    Создаёт бэкап текущих конфигов и данных бота и удаляет самые старые.

    :return: Путь к бэкапу или None, если создать не удалось.
    :rtype: `str` or `None`
    """
    try:
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        path = _backup_path()

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in _all_files():
                if not os.path.exists(file.path):
                    continue
                archive.write(file.path, file.path)

        _rotate_backups()
        return path
    except Exception as e:
        logger.error(f"Не удалось создать бэкап конфигов: {e}")
        return None


def list_backups() -> list[str]:
    """
    Возвращает названия имеющихся бэкапов, от свежего к старому.

    :return: Названия файлов бэкапов.
    :rtype: `list` of `str`
    """
    try:
        # только свои имена: посторонний zip в папке не должен попасть ни в отчёт, ни под ротацию
        backups = [
            name for name in os.listdir(BACKUPS_DIR)
            if name.startswith(BACKUP_PREFIX) and name.lower().endswith(".zip")
        ]
    except:
        return []

    # имя бэкапа лексикографически монотонно, поэтому сортируем по нему, а не по mtime
    backups.sort(reverse=True)
    return backups


def recent_backup() -> str | None:
    """
    Возвращает путь к бэкапу, созданному только что, если такой есть.

    Нужен, чтобы повторные нажатия кнопки не забивали все слоты
    одинаковыми копиями и не вытесняли бэкапы, снятые перед импортом.

    :return: Путь к свежему бэкапу или None, если такого нет.
    :rtype: `str` or `None`
    """
    backups = list_backups()
    if not backups:
        return None

    path = os.path.join(BACKUPS_DIR, backups[0])
    try:
        if time.time() - os.path.getmtime(path) < BACKUP_COOLDOWN:
            return path
    except:
        return None
    return None


def prepare_import_dir(user_id: int | str) -> str:
    """
    Готовит чистую папку под импортируемый файл пользователя.

    :param user_id: ID пользователя Telegram, который прислал файл.
    :type user_id: `int` or `str`

    :return: Путь к папке.
    :rtype: `str`
    """
    return _prepare_dir(_user_dir(user_id, "import"))


def clear_import_dir(user_id: int | str):
    """Удаляет папку с импортируемыми файлами пользователя."""
    _clear_dir(_user_dir(user_id, "import"))


def peek_import(path: str) -> list[str]:
    """
    Смотрит, какие конфиги бота лежат внутри импортируемого файла.

    :param path: Путь к файлу или архиву.
    :type path: `str`

    :return: Названия найденных конфигов.
    :rtype: `list` of `str`
    """
    names = []

    if path.lower().endswith(".json"):
        file = _file_by_json_name(os.path.basename(path))
        if file:
            names.append(file.name)
        return names

    with _open_archive(path) as archive:
        for member_name, _ in _archive_members(archive):
            file = _file_by_json_name(os.path.basename(member_name))
            if file and file.name not in names:
                names.append(file.name)
    return names


def _keep_current_values(file: SettingsFile | DataFile, new: dict, keep_secrets: bool) -> dict:
    if file.name != "config":
        return new

    current = sett.get(file.name) or {}
    paths = list(KEEP_ALWAYS)
    if keep_secrets:
        paths += SECRET_PATHS

    for path in paths:
        value, exists = _get_by_path(current, path)
        if exists:
            _set_by_path(new, path, value)
    return new


def _prepare_json(file: SettingsFile | DataFile, raw: bytes, keep_secrets: bool) -> dict | list:
    try:
        new = json.loads(raw.decode("utf-8-sig"))
    except Exception:
        raise Exception("не читается как JSON")

    if not isinstance(new, type(file.default)):
        expected = "объект" if isinstance(file.default, dict) else "список"
        raise Exception(f"содержимое должно быть {expected}")

    # файлы данных мержить не с чем — у них нет шаблона, кладём как есть
    if isinstance(new, dict) and not _is_data(file):
        new = restore_config(new, file.default)
        new = _keep_current_values(file, new, keep_secrets)
    return new


def import_file(path: str, keep_secrets: bool = True) -> tuple[list[str], list[tuple[str, str]], str | None]:
    """
    Импортирует конфиги и данные бота из файла или архива.
    Бэкап текущих конфигов создаётся только если есть что применить.

    :param path: Путь к .json файлу или .zip / .rar архиву.
    :type path: `str`

    :param keep_secrets: Оставить текущие секретные данные (Cookie-данные, токены, пароль).
    :type keep_secrets: `bool`

    :return: Названия применённых файлов, пропущенные файлы с причинами и путь к бэкапу.
    :rtype: `tuple` of `list` of `str`, `list` of `tuple` of `str` and `str` or `None`
    """
    applied: list[str] = []
    skipped: list[tuple[str, str]] = []
    backup = None
    backup_tried = False

    def handle(member_name: str, size: int, read: callable):
        nonlocal backup, backup_tried
        json_name = os.path.basename(member_name)

        if not json_name.lower().endswith(".json"):
            skipped.append((json_name, "не .json файл"))
            return

        file = _file_by_json_name(json_name)
        if not file:
            skipped.append((json_name, "не конфиг и не данные бота"))
            return

        if json_name.lower() in [name.lower() for name in applied]:
            skipped.append((json_name, "уже импортирован из этого файла"))
            return

        if size > MAX_MEMBER_SIZE:
            skipped.append((json_name, f"слишком большой (максимум {MAX_MEMBER_SIZE // 1024 // 1024} МБ)"))
            return

        try:
            new = _prepare_json(file, read(), keep_secrets)

            if not backup_tried: # бэкапим один раз и только когда есть что писать
                backup_tried = True
                backup = make_backup()

            try:
                _write_file(file, new)
            except Exception as e:
                # сырой OSError тащит в текст юзеру путь и системную формулировку
                logger.error(f"Не удалось записать {file.path} при импорте: {e}")
                raise Exception("не удалось записать файл")

            applied.append(json_name)
        except Exception as e:
            skipped.append((json_name, str(e)))

    if not path.lower().endswith(SUPPORTED_EXTENSIONS):
        raise Exception("❌ Поддерживаются только файлы .json, .zip и .rar")

    size = os.path.getsize(path)
    if size > MAX_IMPORT_SIZE:
        raise Exception(f"❌ Файл слишком большой (максимум {MAX_IMPORT_SIZE // 1024 // 1024} МБ)")

    if path.lower().endswith(".json"):
        with open(path, "rb") as f:
            raw = f.read()
        handle(os.path.basename(path), size, lambda: raw)
    else:
        with _open_archive(path) as archive:
            members = _archive_members(archive)
            if not members:
                raise Exception("❌ Архив пустой")
            for name, member_size in members:
                handle(name, member_size, lambda n=name: _read_member(archive, n))

    if not applied and not skipped:
        raise Exception("❌ В файле не нашлось ни одного конфига или файла данных бота")

    return applied, skipped, backup
