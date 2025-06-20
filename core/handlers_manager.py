from playerokapi.enums import EventTypes

_bot_event_handlers = {
    "ON_MODULE_CONNECTED": [],
    "ON_INIT": [],
    "ON_PLAYEROK_BOT_INIT": [],
    "ON_TELEGRAM_BOT_INIT": []
}
""" Хендлеры ивентов бота. """
_playerok_event_handlers = {
    EventTypes.CHAT_INITIALIZED: [],
    EventTypes.NEW_MESSAGE : [],
    EventTypes.NEW_DEAL : [],
    EventTypes.DEAL_CONFIRMED : [],
    EventTypes.DEAL_ROLLED_BACK : [],
    EventTypes.DEAL_HAS_PROBLEM : [],
    EventTypes.DEAL_PROBLEM_RESOLVED : [],
    EventTypes.DEAL_STATUS_CHANGED : [],
    EventTypes.ITEM_PAID : [],
    EventTypes.ITEM_SENT : []
}
""" Хендлеры ивентов Playerok Listener`а. """

class HandlersManager:
    """
    Класс, описывающий взаимодействие с хендлерами бота.
    """

    @staticmethod
    def set_bot_event_handlers(data: dict[str, list]):
        global _bot_event_handlers
        _bot_event_handlers = data

    @staticmethod
    def get_bot_event_handlers() -> dict[str, list]:
        global _bot_event_handlers
        return _bot_event_handlers

    @staticmethod
    def add_bot_event_handler(event: str, handler):
        global _bot_event_handlers
        _bot_event_handlers[event].append(handler)

    @staticmethod
    def set_playerok_event_handlers(data: dict[EventTypes, list]):
        global _playerok_event_handlers
        _playerok_event_handlers = data

    @staticmethod
    def get_playerok_event_handlers() -> dict[EventTypes, list]:
        global _playerok_event_handlers
        return _playerok_event_handlers
    
    @staticmethod
    def add_playerok_event_handler(event: EventTypes, handler):
        global _playerok_event_handlers
        _playerok_event_handlers[event].append(handler)

    @staticmethod
    def register_bot_event_handlers(handlers):
        """ Устанавливает ивент хендлеры бота. """
        global _bot_event_handlers
        for event_type, funcs in handlers.items():
            if event_type not in _bot_event_handlers:
                _bot_event_handlers[event_type] = []
            _bot_event_handlers[event_type].extend(funcs)

    @staticmethod
    def register_playerok_event_handlers(handlers):
        """ Устанавливает хендлеры фанпей ивентов. """
        global _playerok_event_handlers
        for event_type, funcs in handlers.items():
            if event_type not in _playerok_event_handlers:
                _playerok_event_handlers[event_type] = []
            _playerok_event_handlers[event_type].extend(funcs)

    @staticmethod
    def remove_handlers(bot_event_handlers, playerok_event_handlers):
        """ Удаляет все хендлеры модуля из глобальных списков. """
        global _bot_event_handlers, _playerok_event_handlers
        for event, funcs in bot_event_handlers.items():
            if event in _bot_event_handlers:
                for func in funcs:
                    if func in _bot_event_handlers[event]:
                        _bot_event_handlers[event].remove(func)
        for event, funcs in playerok_event_handlers.items():
            if event in playerok_event_handlers:
                for func in funcs:
                    if func in playerok_event_handlers[event]:
                        playerok_event_handlers[event].remove(func)
        