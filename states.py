"""
Basic states for Request and Waiter
"""

from enum import Enum, auto


class RequestState(Enum):
    WAITING_FOR_WAITER = auto()
    OK = auto()
    WAITING_FOR_BILL = auto()


class WaiterState(Enum):
    DELIVERING_DISH = auto()
    BILLING = auto()
    SERVICING = auto()
    FREE = auto()
