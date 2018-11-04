"""
This module consists of the most important objects of the simulator.
There are restaurant's initialization with custom parameters.
Also average intervals between requests according to current time are calculated.
According to the intervals and probability of count of people requests are generating.
All time in system is in seconds (except user's input).
"""

import json
from restaurant import *
from events import *


class RequestInterval:
    """
    Calculating average intervals between requests according to current time in SECONDS
    """

    def __init__(self, total, item):
        self.fromInterval = item['from'] * 60 * 60
        self.toInterval = item['to'] * 60 * 60
        self.interval = round(1 / (total * item['part'] / (self.toInterval - self.fromInterval)))


class Model:
    """
    Generating of requests (people) and taking a sit
    """

    def run(self):
        while self.global_time < self.work_time_to:
            # for event in self.next_events:
            #  print(str(round(event.when / 3600)) + ":" + str(round(event.when / 60) % 60), event.what.__dict__)

            for event in filter(lambda e: e.when <= self.global_time, self.next_events):
                event.handle(self)
                self.next_events.remove(event)

            # print(str(round(self.global_time / 3600)) + ":" + str(round(self.global_time / 60) % 60))
            self.global_time += 1

    """
    Calculate average interval between requests according to current time
    """

    def current_request_mean(self):
        current_interval = list(filter(
            lambda interval: interval.fromInterval <= self.global_time <= interval.toInterval,
            self.intervals))[0]

        return current_interval.interval

    """
    Add average intervals in a model
    """

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
        self.cooking_time = params['cooking_time']
        service_time = params['service_time']
        mode = params['restaurant_mode']
        self.tables = []
        self.waiters = []
        self.cookers = []
        self.dishes = []

        for table_class in params['tables']:
            for index in range(table_class['count']):
                self.tables.append(Table(table_class['size']))

        for index in range(params['waiters']):
            self.waiters.append(Waiter(service_time * 60))

        for index in range(params['cookers']):
            self.cookers.append(Cooker(self.cooking_time * 60))

        self.work_time_from = mode['work_time']['from'] * 60 * 60  # in seconds
        self.work_time_to = mode['work_time']['to'] * 60 * 60  # in seconds
        self.class_probability = mode['class_probability']
        self.eating_time = mode['eating_time']
        self.intervals = self.init_work_mode(mode)
        self.global_time = self.work_time_from
        self.next_events = []
        self.next_events.append(Event(self.global_time, RequestEvent(1)))
        self.count = 0
        self.lost_counter = 0
