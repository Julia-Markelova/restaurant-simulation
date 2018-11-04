"""
This module consists of the most important objects of the simulator.
There are restaurant's initialization with custom parameters.
Also average intervals between requests according to current time are calculated.
"""

import json
from random import expovariate, choices
from restaurant import *


class RequestInterval:
    """
    Calculating average intervals between requests according to current time in MINUTES
    """

    def __init__(self, total, item):
        self.fromInterval = item['from']
        self.toInterval = item['to']
        self.interval = 60 / (total * item['part'] / (self.toInterval - self.fromInterval))


class Event:
    def __init__(self, when, what):
        self.when = when
        self.what = what


class Model:

    def next_request(self, mean):
        people_count = choices(list(self.class_probability.keys()), list(self.class_probability.values()))
        next_request_time = expovariate(1 / mean)
        request = Request(people_count)
        self.next_events.append(
            Event(
                next_request_time,
                Request(choices(list(self.class_probability.keys()), list(self.class_probability.values())))
            )
        )

        return request

    def run(self):
        pass

    def init_work_mode(self, mode):
        intervals = []

        for item in mode['attendance']:
            intervals.append(RequestInterval(mode['average_per_day'], item))

        return intervals

    """
        Initializing restaurant's parameters
    """

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
        self.global_time = 0
        self.next_events = []
        self.next_events.append(Event(0, self.next_request(self.intervals[0].interval)))
