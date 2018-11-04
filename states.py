from enum import Enum, auto


class State(Enum):
    WAITING = auto()
    OK = auto()
    EATING = auto()