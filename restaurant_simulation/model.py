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
        self. last = item['last'] == "True"

        if item['part'] != 0:
            self.interval = round((self.toInterval - self.fromInterval) / (total * item['part']))
        else:
            self.interval = 0


class Model:

    def run(self):
        """
        Executing events while they are in the system.
        """
        while self.global_time < self.restaurant.work_time_to or self.next_events and \
                not self.restaurant.strict_close:
            interval = self.current_request_interval()

            if interval and interval.fromInterval == self.global_time and self.current_request_mean() != 0:
                self.next_events.append(
                    Event(
                        self.global_time,
                        RequestEvent(Request(1, self.restaurant.reorder_probability, self.global_time))
                    )
                )

            for event in sorted(filter(lambda ev: ev.when <= self.global_time, self.next_events),
                                key=lambda ev: ev.when):
                event.handle(self)
                self.next_events.remove(event)

            length = len(
                list(filter(lambda t: not t.available and t.owner.state == RequestState.WAITING_FOR_WAITER,
                            self.restaurant.tables))
            )
            st.avg_waiting_queue[length] += 1

            length = len(
                list(filter(lambda t: not t.available and t.owner.state == RequestState.WAITING_FOR_BILL,
                            self.restaurant.tables))
            )
            st.avg_billing_queue[length] += 1

            length = len(self.restaurant.ready_dishes)
            st.avg_dishes_queue[length] += 1

            self.global_time += 1

        logging.info("%s: Restaurant is closing",
                     human_readable_date_time(self.global_time))

    def request_interval(self, time):
        suitable_intervals = list(
            filter(
                lambda interval: interval.fromInterval <= time,
                self.intervals)
        )

        return max(suitable_intervals, key=lambda interval: interval.fromInterval)

    def current_request_interval(self):
        return self.request_interval(self.global_time)

    def current_request_mean(self):
        """
        :return: average interval in seconds
        """
        current_interval = self.current_request_interval()

        return current_interval.interval

    def __init__(self, data):
        """
        Initializing restaurant_simulation's parameters
        Calculating average interval between requests according to current time
        Adding average intervals in a model
        :param data: json file with params
        """
        params = json.load(data)
        self.intervals = []

        for item in params['restaurant_mode']['attendance']:
            self.intervals.append(RequestInterval(params['restaurant_mode']['average_per_day'], item))

        self.restaurant = Restaurant(params, self.intervals)
        self.global_time = self.restaurant.work_time_from
        self.class_probability = params['restaurant_mode']['class_probability']
        self.next_events = []
