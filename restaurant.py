class Table:
    def __init__(self, size):
        self.size = size
        self.available = True
        self.owner = None


class Waiter:
    def __init__(self, service_time):
        self.service_time = service_time
        self.available = True


class Cooker:
    def __init__(self, cooking_time):
        self.cooking_time = cooking_time


class Dish:
    def __init__(self, request):
        self.is_ready = False
        self.request = request
