import io
import re
import sys
import logging
import threading
from datetime import datetime

from rich import box
from rich.console import Console, Group
from rich.control import Control
from rich.panel import Panel
from rich.segment import ControlType
from rich.table import Table
from rich.text import Text


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
# PREFIX модулей: цвет + имя + серая точка — «autostars ·»; имя уезжает в колонку источника
PREFIX_RE = re.compile(r"^((?:\x1b\[[0-9;]*m)*\s*)([\w.\-]+)\s*((?:\x1b\[[0-9;]*m)*)\s*·\s*((?:\x1b\[[0-9;]*m)*)\s?")
CORE_LOGGERS = ("universal", "root")
SOURCE_WIDTH = 15
PLAIN_WIDTH = 100
NOTICE_DELAY = 3

LEVEL_ICONS = {
    logging.DEBUG: ("·", "grey50"),
    logging.INFO: ("●", "green"),
    logging.WARNING: ("▲", "yellow"),
    logging.ERROR: ("■", "red"),
    logging.CRITICAL: ("■", "bold red")
}
ASCII_ICONS = {logging.DEBUG: ".", logging.INFO: "*", logging.WARNING: "!", logging.ERROR: "x", logging.CRITICAL: "X"}

_console: Console | None = None
_lock = threading.RLock()
_last_date = None
_notices: dict[str, dict] = {}
_notices_lock = threading.Lock()
_prompt: str | None = None # подпись строки ввода, которая сейчас висит внизу консоли


def get_console() -> Console:
    global _console
    if _console is None:
        tty = sys.stdout.isatty()
        file = None
        encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
        if not encoding.startswith("utf"):
            try: # консоль не в UTF-8: рамки rich сам заменит на ASCII, а эмодзи станут «?» вместо падения
                file = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding or "ascii", errors="replace", line_buffering=True)
            except Exception:
                file = None
        # без терминала (systemd, journal) rich не знает ширину — берём фиксированную, иначе таблицы сожмутся до 80
        _console = Console(file=file, highlight=False, emoji=False, width=None if tty else 110, soft_wrap=False)
    return _console


def set_console(console: Console):
    global _console, _last_date
    _console = console
    _last_date = None


def is_ascii() -> bool:
    return not (get_console().encoding or "").lower().startswith("utf")


def _text(value) -> Text:
    if isinstance(value, Text):
        return value
    return Text.from_ansi(str(value)) # цвета colorama в строках сохраняются, а [скобки] не съедаются как разметка rich


def _source(record: logging.LogRecord, message: str) -> tuple[Text, str]:
    name = record.name
    if name.split(".")[0] in CORE_LOGGERS or name.startswith(("aiogram", "urllib3", "asyncio")):
        return Text(""), message
    if name.startswith("modules."):
        name = name.split(".")[1]

    match = PREFIX_RE.match(message)
    if match:
        source = Text.from_ansi(match.group(1) + match.group(2))
        source.stylize("bold")
        return source, match.group(4) + message[match.end():] # цвет, заданный после точки, относится уже к тексту
    return Text(name, style="bold white"), message


def _line(record: logging.LogRecord, source: Text, message: str) -> Table:
    if is_ascii():
        icon = Text(ASCII_ICONS.get(record.levelno, "*"), style=LEVEL_ICONS.get(record.levelno, ("", "white"))[1])
    else:
        char, style = LEVEL_ICONS.get(record.levelno, ("●", "white"))
        icon = Text(char, style=style)

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="grey46", no_wrap=True)
    grid.add_column(no_wrap=True)
    grid.add_column(no_wrap=True, width=SOURCE_WIDTH)
    grid.add_column(overflow="fold") # перенос длинного текста встаёт под колонку сообщения, а не под время
    grid.add_row(
        datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
        icon,
        source,
        _text(message)
    )
    return grid


def _print_date(created: float):
    global _last_date
    date = datetime.fromtimestamp(created).date()
    if date != _last_date:
        _last_date = date
        get_console().print(Text(f"── {date.strftime('%d.%m.%Y')} ──", style="grey46"))


class ConsoleHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            message = record.getMessage()
            if record.exc_info:
                message += "\n" + logging.Formatter().formatException(record.exc_info)
            renderable = getattr(record, "renderable", None)
            empty = not ANSI_RE.sub("", message).strip()
            if empty and renderable is None: # logger.info("") модули ставили как разделитель — в новой консоли он лишний
                return

            source, message = _source(record, message)
            with _lock: # одна запись — один неразрывный блок, даже если логируют сразу из нескольких потоков
                console = get_console()
                _erase_prompt(console)
                _print_date(record.created)
                if not empty and ANSI_RE.sub("", message).strip():
                    console.print(_line(record, source, message))
                if renderable is not None:
                    console.print(renderable)
                _draw_prompt(console)
        except Exception:
            self.handleError(record)


def render_plain(renderable, width: int = PLAIN_WIDTH) -> str:
    buffer = io.StringIO()
    Console(file=buffer, width=width, color_system=None, force_terminal=False, emoji=False, highlight=False).print(renderable)
    return buffer.getvalue().rstrip("\n")


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = ANSI_RE.sub("", super().format(record))
        renderable = getattr(record, "renderable", None)
        if renderable is not None:
            message += "\n" + render_plain(renderable)
        return message


def kv_grid(rows: list[tuple]) -> Table:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="grey62", no_wrap=True)
    grid.add_column(style="bright_white", overflow="fold")
    for key, value in rows:
        grid.add_row(_text(key), _text(value))
    return grid


def _title(title, color: str) -> Text | None:
    if not title:
        return None
    text = _text(title).copy()
    if not text.spans: # заголовок без своих цветов — красим в цвет рамки
        text.stylize(color)
    text.stylize("bold")
    return text


def make_panel(title, body, color: str = "yellow", width: int = None) -> Panel:
    if isinstance(body, (list, tuple)):
        body = kv_grid(body)
    elif isinstance(body, str):
        body = _text(body)
    return Panel(
        body,
        title=_title(title, color),
        title_align="left",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1),
        width=width,
        expand=width is not None # по содержимому, а не во всю ширину окна
    )


def make_table(title, columns: list, rows: list[list], color: str = "bright_blue") -> Table:
    table = Table(
        title=_title(title, color),
        title_justify="left",
        box=box.ROUNDED,
        border_style=color,
        header_style=f"bold {color}",
        padding=(0, 1)
    )
    for column in columns:
        table.add_column(_text(column))
    for row in rows:
        table.add_row(*[_text(cell) for cell in row])
    return table


def print_line(text: str, level: int = logging.INFO):
    # строка в стиле лога, но мимо логгера — для консольной настройки, где логгер ещё не настроен
    record = logging.LogRecord("universal", level, "", 0, text, None, None)
    with _lock:
        console = get_console()
        _erase_prompt(console)
        _print_date(record.created)
        console.print(_line(record, Text(""), text))
        _draw_prompt(console)


def print_panel(title, body, color: str = "yellow", width: int = None):
    with _lock:
        console = get_console()
        _erase_prompt(console)
        console.print(make_panel(title, body, color, width))
        _draw_prompt(console)


def _erase_prompt(console: Console):
    if _prompt is not None:
        console.control(Control(ControlType.CARRIAGE_RETURN, (ControlType.ERASE_IN_LINE, 2)))


def _draw_prompt(console: Console):
    # строка ввода в той же сетке, что и лог: время, иконка, «ввод» в колонке источника, стрелка в колонке текста
    if _prompt is None:
        return
    ascii_mode = is_ascii()
    line = Text()
    line.append(datetime.now().strftime("%H:%M:%S"), style="grey46")
    line.append("  ")
    line.append("?" if ascii_mode else "✎", style="bold bright_cyan")
    line.append("  ")
    line.append(_prompt.ljust(SOURCE_WIDTH), style="bold bright_cyan")
    line.append("  ")
    line.append("> " if ascii_mode else "→ ", style="bold bright_yellow")
    console.print(line, end="")
    console.file.flush()


def show_prompt(label: str = "ввод"):
    # пока приглашение висит, всё, что печатается в консоль, встаёт над ним, а оно перерисовывается снизу
    global _prompt
    with _lock:
        if _prompt is None:
            _prompt = label
            _draw_prompt(get_console())


def hide_prompt(erase: bool = True):
    # erase=False — когда юзер уже нажал Enter и курсор сам ушёл на новую строку
    global _prompt
    with _lock:
        if erase:
            _erase_prompt(get_console())
        _prompt = None


def log_panel(logger: logging.Logger, title, rows=None, message: str = "", level: int = logging.INFO,
              color: str = "yellow", width: int = None, body=None):
    """
    Пишет в лог панель «ключ — значение» одной записью: в консоли — рамка, в latest.log — она же текстом.

    :param logger: Логгер модуля.
    :type logger: `logging.Logger`

    :param title: Заголовок панели (можно с цветами colorama).
    :type title: `str`

    :param rows: Строки панели — пары (ключ, значение), _опционально_.
    :type rows: `list` of `tuple`

    :param message: Строка лога над панелью, _опционально_.
    :type message: `str`

    :param level: Уровень лога, _опционально_.
    :type level: `int`

    :param color: Цвет рамки (имя цвета rich), _опционально_.
    :type color: `str`

    :param body: Готовый текст или renderable rich вместо rows, _опционально_.
    """
    panel = make_panel(title, body if body is not None else (rows or []), color, width)
    logger.log(level, message, extra={"renderable": panel})


def log_table(logger: logging.Logger, title, columns: list, rows: list[list], message: str = "",
              level: int = logging.INFO, color: str = "bright_blue"):
    """
    Пишет в лог таблицу одной записью.

    :param logger: Логгер модуля.
    :type logger: `logging.Logger`

    :param title: Заголовок таблицы.
    :type title: `str`

    :param columns: Названия колонок.
    :type columns: `list` of `str`

    :param rows: Строки таблицы.
    :type rows: `list` of `list`
    """
    logger.log(level, message, extra={"renderable": make_table(title, columns, rows, color)})


def log_notice(logger: logging.Logger, group: str, title: str, item, lines: list = (), level: int = logging.WARNING,
               color: str = "red", label: str = "", delay: float = NOTICE_DELAY):
    """
    Сгруппированное уведомление: одинаковые group от разных модулей за delay секунд
    сливаются в одну панель со списком item'ов вместо десятка одинаковых блоков.

    :param logger: Логгер модуля.
    :type logger: `logging.Logger`

    :param group: Ключ группы — уведомления с одним ключом объединяются.
    :type group: `str`

    :param title: Заголовок панели.
    :type title: `str`

    :param item: Что затронуто — обычно имя модуля (можно с цветом).
    :type item: `str`

    :param lines: Общие для группы строки, например инструкция, _опционально_.
    :type lines: `list` of `str`

    :param label: Подпись перед списком item'ов, _опционально_.
    :type label: `str`
    """
    with _notices_lock:
        notice = _notices.get(group)
        if notice is None:
            notice = _notices[group] = {
                "logger": logger, "title": title, "items": [], "lines": list(lines),
                "level": level, "color": color, "label": label
            }
            timer = threading.Timer(delay, _flush_notice, (group,))
            timer.daemon = True
            timer.start()
        if all(_text(item).plain != _text(i).plain for i in notice["items"]):
            notice["items"].append(item)


def _flush_notice(group: str):
    with _notices_lock:
        notice = _notices.pop(group, None)
    if not notice:
        return

    items = Text(", ").join(_text(item) for item in notice["items"])
    body = [Text.assemble(_text(notice["label"]), items)] if notice["label"] else [items]
    if notice["lines"]:
        body.append(Text(""))
        body += [_text(line) for line in notice["lines"]]

    title = Text.assemble(_text(notice["title"]), (f" · {len(notice['items'])}", "grey62"))
    title.stylize(f"bold {notice['color']}", 0, len(title.plain) - len(f" · {len(notice['items'])}"))
    logger = notice["logger"] if len(notice["items"]) == 1 else logging.getLogger("universal.notice")
    logger.log(notice["level"], "", extra={"renderable": make_panel(title, Group(*body), notice["color"])})
