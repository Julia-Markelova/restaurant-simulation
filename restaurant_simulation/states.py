"""
Basic states for Request and Waiter
"""

from enum import Enum, auto


class RequestState(Enum):
    WAITING_FOR_WAITER = auto()
    LEAVING_BAD_MENU = auto()
    OK = auto()
    EATING = auto()
    WAITING_FOR_BILL = auto()


class WaiterState(Enum):
    DELIVERING_DISH = auto()
    BILLING = auto()
    SERVICING = auto()
    FREE = auto()
