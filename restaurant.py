"""
Module describes the main params of the restaurant.
"""

from states import State


class Restaurant:
    def __init__(self, params):
        self.tables = []
        self.waiters = []
        self.cookers = []
        self.ready_dishes = []
        self.waiting_dishes = []
        self.bill = []

        for table_class in params['tables']:
            for index in range(table_class['count']):
                self.tables.append(Table(table_class['size']))

        for index in range(params['waiters']):
            self.waiters.append(Waiter(params['service_time'] * 60))

        for index in range(params['cookers']):
            self.cookers.append(Cooker(params['cooking_time'] * 60))

        self.eating_time = params['restaurant_mode']['eating_time']
        self.work_time_from = params['restaurant_mode']['work_time']['from'] * 60 * 60  # in seconds
        self.work_time_to = params['restaurant_mode']['work_time']['to'] * 60 * 60  # in seconds


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
        self.available = True


class Request:
    def __init__(self, size, c):
        self.c = c
        self.size = size
        self.table = None
        self.status = State.OK


class Dish:
    def __init__(self, request):
        self.is_ready = False
        self.request = request
