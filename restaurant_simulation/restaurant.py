"""
Module describes the main params of the restaurant_simulation.
"""

from itertools import count

from restaurant_simulation import kitchen, waiters


class Restaurant:
    def __init__(self, params, intervals):
        """
        Initializing restaurant_simulation with custom parameters
        :param params: parsed json file
        """
        self.tables = []
        self.waiters = []
        self.cookers = []
        self.ready_dishes = []
        self.waiting_dishes = []

        for table_class in params['tables']:
            for index in range(table_class['count']):
                self.tables.append(Table(table_class['size']))

        for index in range(0, params['waiters']):
            self.waiters.append(waiters.Waiter(params['service_time'] * 60, intervals))

        for index in range(0, params['cookers']):
            self.cookers.append(kitchen.Cooker(params['cooking_time'] * 60, intervals))

        self.eating_time = params['restaurant_mode']['eating_time'] * 60
        self.waiting_time = params['waiting_time'] * 60
        self.delivery_time = params['delivery_time'] * 60
        self.thinking_time = params['thinking_time'] * 60
        self.work_time_from = params['restaurant_mode']['work_time']['from'] * 60 * 60  # in seconds
        self.work_time_to = params['restaurant_mode']['work_time']['to'] * 60 * 60  # in seconds
        self.last_entrance_time = params['restaurant_mode']['work_time']['last_entrance_time'] * 60 * 60
        self.reorder_probability = params['reorder_probability']
        self.leaving_probability = params['leaving_probability']
        self.over_work_time_limit = params['restaurant_mode']['work_time']['over_work_time_limit'] * 60 * 60
        self.strict_close = params['restaurant_mode']['work_time']['strict_close'] == "True"

        if self.strict_close:
            self.work_time_to += self.over_work_time_limit


class Table:
    _ids = count(1)

    def __init__(self, size):
        """
        Constructor for tables in restaurant_simulation
        :param size: how many people can sit on the table
        """
        self.size = size
        self.available = True
        self.owner = None
        self.id = next(self._ids)