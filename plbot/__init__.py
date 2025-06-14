from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .playerokbot import PlayerokBot

_playerok_bot: 'PlayerokBot' = None

def get_playerok_bot() -> 'PlayerokBot':
    global _playerok_bot
    return _playerok_bot

def set_playerok_bot(new: 'PlayerokBot') -> 'PlayerokBot':
    global _playerok_bot
    _playerok_bot = new