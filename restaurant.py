
class Table:
    def __init__(self, size):
        self.size = size
        self.available = True


class Waiter:
    def __init__(self, service_time):
        self.service_time = service_time
        self.available = True


class Cooker:
    def __init__(self, cooking_time):
        self.cooking_time = cooking_time


class Request:
    def __init__(self, size, probability, eating_time):
        self.size = size
        self.probability = probability
        self.eating_time = eating_time
