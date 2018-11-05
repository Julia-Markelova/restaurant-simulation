"""
Module describes the main params of the restaurant.
"""

from states import RequestState, WaiterState
from itertools import count


class Restaurant:
    def __init__(self, params):
        self.tables = []
        self.waiters = []
        self.cookers = []
        self.ready_dishes = []
        self.waiting_dishes = []

        for table_class in params['tables']:
            for index in range(table_class['count']):
                self.tables.append(Table(table_class['size']))

        for index in range(params['waiters']):
            self.waiters.append(Waiter(params['service_time'] * 60))

        for index in range(params['cookers']):
            self.cookers.append(Cooker(params['cooking_time'] * 60))

        self.eating_time = params['restaurant_mode']['eating_time'] * 60
        self.waiting_time = params['waiting_time'] * 60
        self.delivery_time = params['delivery_time'] * 60
        self.thinking_time = params['thinking_time'] * 60
        self.work_time_from = params['restaurant_mode']['work_time']['from'] * 60 * 60  # in seconds
        self.work_time_to = params['restaurant_mode']['work_time']['to'] * 60 * 60  # in seconds
        self.last_entrance_time = params['restaurant_mode']['work_time']['last_entrance_time'] * 60 * 60


class Table:
    _ids = count(1)

    def __init__(self, size):
        self.size = size
        self.available = True
        self.owner = None
        self.id = next(self._ids)


class Waiter:
    _ids = count(1)

    def __init__(self, service_time):
        self.service_time = service_time
        self.id = next(self._ids)
        self.state = WaiterState.FREE


class Cooker:
    _ids = count(1)

    def __init__(self, cooking_time):
        self.cooking_time = cooking_time
        self.available = True
        self.id = next(self._ids)


class Request:
    _ids = count(1)

    def __init__(self, size):
        self.id = next(self._ids)
        self.size = size
        self.table = None
        self.state = RequestState.OK
        self.dish_count = 0


class Dish:
    _ids = count(1)

    def __init__(self, request):
        self.request = request
        self.id = next(self._ids)
