"""
This module consists of the most important objects of the simulator.
There are restaurant's initialization with custom parameters.
Also average intervals between requests according to current time are calculated.
According to the intervals and probability of count of people requests are generating.
"""

import json
from restaurant import *
from generating import *


class RequestInterval:
    """
    Calculating average intervals between requests according to current time in MINUTES
    """

    def __init__(self, total, item):
        self.fromInterval = item['from']
        self.toInterval = item['to']
        self.interval = 60 / (total * item['part'] / (self.toInterval - self.fromInterval))


class Model:

    def run(self):
        while self.global_time < self.work_time_to:
            for event in filter(lambda e: e.when == self.global_time, self.next_events):
                event.handle(self)
                self.next_events.remove(event)

            self.global_time += 1

    def current_request_mean(self):
        current_interval = list(filter(
            lambda interval:
            interval.fromInterval * 60 * 60 < self.work_time_from +
            self.global_time < interval.toInterval * 60 * 60,
            self.intervals))[0]

        return current_interval.interval

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
        # in seconds
        self.work_time_from = mode['work_time']['from'] * 60 * 60
        self.work_time_to = mode['work_time']['to'] * 60 * 60
        self.class_probability = mode['class_probability']
        self.eating_time = mode['eating_time']
        self.intervals = self.init_work_mode(mode)
        self.global_time = 0
        self.next_events = []
        self.next_events.append(Event(0, Request(1)))
