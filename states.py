from enum import Enum, auto


class State(Enum):
    WAITING_FOR_WAITER = auto()
    OK = auto()
    WAITING_FOR_BILL = auto()
