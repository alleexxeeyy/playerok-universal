from playerokapi.enums import EventTypes


_bot_event_handlers: dict[str, list[callable]] = {
    "ON_MODULE_CONNECTED": [],
    "ON_INIT": [],
    "ON_PLAYEROK_BOT_INIT": [],
    "ON_TELEGRAM_BOT_INIT": []
}
_playerok_event_handlers: dict[EventTypes, list[callable]] = {
    EventTypes.CHAT_INITIALIZED: [],
    EventTypes.NEW_MESSAGE : [],
    EventTypes.NEW_DEAL : [],
    EventTypes.NEW_REVIEW : [],
    EventTypes.DEAL_CONFIRMED : [],
    EventTypes.DEAL_ROLLED_BACK : [],
    EventTypes.DEAL_HAS_PROBLEM : [],
    EventTypes.DEAL_PROBLEM_RESOLVED : [],
    EventTypes.DEAL_STATUS_CHANGED : [],
    EventTypes.ITEM_PAID : [],
    EventTypes.ITEM_SENT : []
}


def set_bot_event_handlers(data: dict[str, list[callable]]):
    """
    Устанавливает новые хендлеры ивентов бота.

    :param data: Словарь с названиями событий и списками хендлеров.
    :type data: `dict[str, list[callable]]`
    """
    global _bot_event_handlers
    _bot_event_handlers = data


def add_bot_event_handler(event: str, handler: callable):
    """
    Добавляет новый хендлер в ивенты бота.

    :param event: Название события, для которого добавляется хендлер.
    :type event: `str`

    :param handler: Вызываемый метод.
    :type handler: `callable`
    """
    global _bot_event_handlers
    _bot_event_handlers[event].append(handler)


def register_bot_event_handlers(handlers: dict[str, list[callable]]):
    """
    Регистрирует хендлеры ивентов бота (добавляет переданные хендлеры, если их нету). 

    :param data: Словарь с названиями событий и списками хендлеров.
    :type data: `dict[str, list[callable]]`
    """
    global _bot_event_handlers
    for event_type, funcs in handlers.items():
        if event_type not in _bot_event_handlers:
            _bot_event_handlers[event_type] = []
        _bot_event_handlers[event_type].extend(funcs)


def get_bot_event_handlers() -> dict[str, list[callable]]:
    """
    Возвращает хендлеры ивентов бота.

    :return: Словарь с событиями и списками хендлеров.
    :rtype: `dict[str, list[callable]]`
    """
    return _bot_event_handlers


def set_playerok_event_handlers(data: dict[EventTypes, list[callable]]):
    """
    Устанавливает новые хендлеры ивентов Playerok.

    :param data: Словарь с событиями и списками хендлеров.
    :type data: `dict[PlayerokAPI.updater.events.EventTypes, list[callable]]`
    """
    global _playerok_event_handlers
    _playerok_event_handlers = data


def add_playerok_event_handler(event: EventTypes, handler: callable):
    """
    Добавляет новый хендлер в ивенты Playerok.

    :param event: Событие, для которого добавляется хендлер.
    :type event: `PlayerokAPI.updater.events.EventTypes`

    :param handler: Вызываемый метод.
    :type handler: `callable`
    """
    global _playerok_event_handlers
    _playerok_event_handlers[event].append(handler)


def register_playerok_event_handlers(handlers):
    """
    Регистрирует хендлеры ивентов Playerok (добавляет переданные хендлеры, если их нету). 

    :param data: Словарь с событиями и списками хендлеров.
    :type data: `dict[PlayerokAPI.updater.events.EventTypes, list[callable]]`
    """
    global _playerok_event_handlers
    for event_type, funcs in handlers.items():
        if event_type not in _playerok_event_handlers:
            _playerok_event_handlers[event_type] = []
        _playerok_event_handlers[event_type].extend(funcs)


def get_playerok_event_handlers() -> dict[EventTypes, list]:
    """
    Возвращает хендлеры ивентов Playerok.

    :return: Словарь с событиями и списками хендлеров.
    :rtype: `dict[PlayerokAPI.updater.events.EventTypes, list[callable]]`
    """
    return _playerok_event_handlers


def remove_handlers(bot_event_handlers: dict[str, list[callable]], playerok_event_handlers: dict[EventTypes, list[callable]]):
    """
    Удаляет переданные хендлеры бота и Playerok.

    :param bot_event_handlers: Словарь с событиями и списками хендлеров бота.
    :type bot_event_handlers: `dict[str, list[callable]]`

    :param playerok_event_handlers: Словарь с событиями и списками хендлеров Playerok.
    :type playerok_event_handlers: `dict[PlayerokAPI.updater.events.EventTypes, list[callable]]`
    """ # ДОДЕЛАТЬ
    global _bot_event_handlers, _playerok_event_handlers
    for event, funcs in bot_event_handlers.items():
        if event in _bot_event_handlers:
            for func in funcs:
                if func in _bot_event_handlers[event]:
                    _bot_event_handlers[event].remove(func)
    for event, funcs in playerok_event_handlers.items():
        if event in _playerok_event_handlers:
            for func in funcs:
                if func in _playerok_event_handlers[event]:
                    _playerok_event_handlers[event].remove(func)