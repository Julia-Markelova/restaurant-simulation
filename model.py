import json
from restaurant import *


class Model:

    def __init__(self, data):
        params = json.load(data)
        cooking_time = params['cooking_time']
        service_time = params['service_time']
        self.tables = []

        for table_class in params['tables']:
            self.tables.extend([Table(table_class['size'])] * table_class['count'])

        self.waiters = [Waiter(service_time)] * params['waiters']
        self.cookers = [Cooker(cooking_time)] * params['cookers']
        self.requests = params['requests']
