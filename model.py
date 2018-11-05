"""
This module consists of the most important objects of the simulator.
There are restaurant's initialization with custom parameters.
Also average intervals between requests according to current time are calculated.
According to the intervals and probability of count of people requests are generating.
All time in system is in seconds (except user's input).
"""

import json
from restaurant import *
from events.request_event import *


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

    def human_time(self):
        human_time = str(round(self.global_time / 3600)) + ":"

        if len(str(round(self.global_time / 60) % 60)) == 2:
            human_time += str(round(self.global_time / 60) % 60) + ":"
        else:
            human_time += "0" + str(round(self.global_time / 60) % 60) + ":"

        if len(str(round(self.global_time) % 60)) == 2:
            human_time += str(round(self.global_time) % 60)
        else:
            human_time += "0" + str(round(self.global_time) % 60)

        return human_time

    def run(self):
        while self.global_time < self.restaurant.work_time_to:

            for event in filter(lambda e: e.when <= self.global_time, self.next_events):
                event.handle(self)
                self.next_events.remove(event)

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
        self.restaurant = Restaurant(params)
        self.global_time = self.restaurant.work_time_from
        self.intervals = self.init_work_mode(params['restaurant_mode'])
        self.class_probability = params['restaurant_mode']['class_probability']
        self.next_events = [e.Event(self.global_time, RequestEvent(Request(1, 1)))]

        self.serviced = 0
        self.count = 0
        self.lost_counter = 0
        self.all = 0
