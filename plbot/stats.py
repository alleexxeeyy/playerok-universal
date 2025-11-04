from datetime import datetime
from dataclasses import dataclass


@dataclass
class Stats:
    bot_launch_time: datetime
    deals_completed: int
    deals_refunded: int
    earned_money: int

        
_stats = Stats(
    bot_launch_time=None,
    deals_completed=0,
    deals_refunded=0,
    earned_money=0
)


def get_stats() -> Stats:
    return _stats


def set_stats(new):
    global _stats
    _stats = new