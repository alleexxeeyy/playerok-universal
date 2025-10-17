from datetime import datetime


class Stats:
    def __init__(
            self, 
            bot_launch_time, 
            deals_completed, 
            deals_refunded,
            earned_money
        ):
        self.bot_launch_time: datetime = bot_launch_time 
        self.deals_completed: int = deals_completed
        self.deals_refunded: int = deals_refunded
        self.earned_money: int = earned_money

        
_stats = Stats(
    bot_launch_time=None,
    deals_completed=0,
    deals_refunded=0,
    earned_money=0
)

def get_stats() -> Stats:
    global _stats
    return _stats

def set_stats(new):
    global _stats
    _stats = new