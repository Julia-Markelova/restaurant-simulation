import json


class Model:
    def __init__(self, data):
        params = json.load(data)
        self.tables = params['tables']
        self.waiters = params['waiters']
        self.cookers = params['cookers']
        self.requests = params['requests']
        self.cooking_time = params['cooking_time']
        self.service_time = params['service_time']
        self.eating_time = params['eating_time']
