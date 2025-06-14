from . import types
from . import parser

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .account import Account

_account: 'Account' = None

def get_account() -> 'Account':
    global _account
    return _account

def set_account(value: 'Account') -> 'Account':
    global _account
    _account = value