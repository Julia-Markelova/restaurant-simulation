"""
This module consists of the most important objects of the simulator.
There are restaurant_simulation's initialization with custom parameters.
Also average intervals between requests according to current time are calculated.
All time in system is in seconds (except user's input).
"""

import json

from restaurant_simulation.event import Event
from restaurant_simulation.restaurant import Restaurant
from restaurant_simulation.visitors import *


class RequestInterval:

    def __init__(self, total, item):
        """
        Calculating average intervals between requests according to current time in SECONDS
        :param total: how many people are coming every day (average meaning)
        :param item: consists of time interval and a part of people which will come in this interval
        """
        self.fromInterval = item['from'] * 60 * 60
        self.toInterval = item['to'] * 60 * 60
        self.interval = round(1 / (total * item['part'] / (self.toInterval - self.fromInterval)))


class Model:

    def run(self):
        """
        Executing events while they are in the system.
        """
        while self.global_time < self.restaurant.work_time_to or self.next_events:

            for event in sorted(filter(lambda ev: ev.when <= self.global_time, self.next_events),
                                key=lambda ev: ev.when):
                event.handle(self)
                self.next_events.remove(event)

            self.global_time += 1

    def current_request_mean(self):
        """

        :return: average interval in seconds
        """
        current_interval = list(
            filter(
                lambda interval: interval.fromInterval <= self.global_time <= interval.toInterval,
                self.intervals)
        )[0]

        return current_interval.interval

    def __init__(self, data):
        """
        Initializing restaurant_simulation's parameters
        Calculating average interval between requests according to current time
        Adding average intervals in a model
        :param data: json file with params
        """
        params = json.load(data)
        self.restaurant = Restaurant(params)
        self.global_time = self.restaurant.work_time_from
        self.intervals = []

        for item in params['restaurant_mode']['attendance']:
            self.intervals.append(RequestInterval(params['restaurant_mode']['average_per_day'], item))

        self.class_probability = params['restaurant_mode']['class_probability']
        self.next_events = [Event(self.global_time,
                                  RequestEvent(Request(1, self.restaurant.reorder_probability,
                                                       self.global_time)))]
