"""
This module consists of the most important objects of the simulator.
There are restaurant's initialization with custom parameters.
Also average intervals between requests according to current time are calculated.
All time in system is in seconds (except user's input).
"""

import json
from restaurant import *
from events.request_event import *


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
    """
    Generating of requests
    """

    def human_time(self):
        """
        Convert global time in the system to the human-readable time
        :return: human-readable time as a string
        """
        day = str(self.global_time // (3600 * 24) + 1)
        hours = str(self.global_time // 3600 % 24)
        minutes = str((self.global_time // 60) % 60)
        seconds = str(self.global_time % 60)

        if len(minutes) != 2:
            minutes = "0" + minutes

        if len(seconds) != 2:
            seconds = "0" + seconds

        return "Day " + day + " " + hours + ":" + minutes + ":" + seconds

    def run(self):
        """
        Executing events while they are in the system.
        """
        while self.global_time < self.restaurant.work_time_to or self.next_events:

            for event in filter(lambda ev: ev.when <= self.global_time, self.next_events):
                event.handle(self)
                self.next_events.remove(event)

            self.global_time += 1

    def current_request_mean(self):
        """
        Calculate average interval between requests according to current time
        :return: average interval in seconds
        """
        current_interval = list(
            filter(
                lambda interval: interval.fromInterval <= self.global_time <= interval.toInterval,
                self.intervals)
        )[0]

        return current_interval.interval

    def init_work_mode(self, mode):
        """
        Add average intervals in a model
        :param mode: restaurant params in json
        :return: a list with average interval and its time
        """
        intervals = []

        for item in mode['attendance']:
            intervals.append(RequestInterval(mode['average_per_day'], item))

        return intervals

    def __init__(self, data):
        """
        Initializing restaurant's parameters
        :param data: json file with params
        """
        params = json.load(data)
        self.restaurant = Restaurant(params)
        self.global_time = self.restaurant.work_time_from
        self.intervals = self.init_work_mode(params['restaurant_mode'])
        self.class_probability = params['restaurant_mode']['class_probability']
        self.next_events = [e.Event(self.global_time,
                                    RequestEvent(Request(1, self.restaurant.reorder_probability)))]

        self.bad_leave_counter = 0
        self.serviced = 0
        self.seated_count = 0
        self.lost_counter = 0
        self.reordered = 0
        self.all = 0
