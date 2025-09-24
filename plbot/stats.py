from datetime import datetime


class Stats:
    def __init__(
            self, 
            bot_launch_time, 
            orders_completed, 
            orders_refunded,
            active_orders,
            earned_money
        ):
        self.bot_launch_time: datetime = bot_launch_time 
        self.orders_completed: int = orders_completed
        self.orders_refunded: int = orders_refunded
        self.active_orders: int = active_orders
        self.earned_money: int = earned_money

        
_stats = Stats(
    bot_launch_time=None,
    orders_completed=0,
    orders_refunded=0,
    active_orders=0,
    earned_money=0
)

def get_stats() -> Stats:
    global _stats
    return _stats

def set_stats(new):
    global _stats
    _stats = new