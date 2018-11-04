import json
from restaurant import *


class RequestInterval:
    def __init__(self, total, item):
        self.fromInterval = item['from']
        self.toInterval = item['to']
        # interval in minutes
        self.interval = 60 / (total * item['part'] / (self.toInterval - self.fromInterval))


class Model:

    def next_request(self):
        pass

    def init_work_mode(self, mode):
        intervals = []

        for item in mode['attendance']:
            intervals.append(RequestInterval(mode['average_per_day'], item))

        return intervals

    def __init__(self, data):
        params = json.load(data)
        cooking_time = params['cooking_time']
        service_time = params['service_time']
        mode = params['restaurant_mode']
        self.tables = []

        for table_class in params['tables']:
            self.tables.extend([Table(table_class['size'])] * table_class['count'])

        self.waiters = [Waiter(service_time)] * params['waiters']
        self.cookers = [Cooker(cooking_time)] * params['cookers']
        self.work_time = mode['work_time']
        self.class_probability = mode['class_probability']
        self.eating_time = mode['eating_time']
        self.intervals = self.init_work_mode(mode)
