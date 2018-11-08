"""
Cooker's logic is here.
"""

import logging
import sys
from itertools import count
from random import expovariate

from restaurant_simulation.event import Event
from restaurant_simulation.states import WaiterState
from restaurant_simulation.utils import human_readable_time

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


class Cooker:
    _ids = count(1)

    def cook(self, model, dish):
        self.available = False
        logging.info("%s: Cooker %d started cooking dish %d for request %d", human_readable_time(model.global_time),
                     self.id, dish.id, dish.request.id)
        cooking_time = expovariate(1 / self.cooking_time)
        model.restaurant.waiting_dishes.remove(dish)
        model.next_events.append(Event(model.global_time + round(cooking_time), DishEvent(dish, self)))

    def __init__(self, cooking_time):
        """
        Constructor for waiters in a restaurant_simulation
        :param cooking_time: average time to cook a dish
        """
        self.cooking_time = cooking_time
        self.available = True
        self.id = next(self._ids)


class CookerCallEvent:

    def handle(self, model):
        model.restaurant.waiting_dishes.append(self.dish)
        cookers = list(filter(lambda c: c.available, model.restaurant.cookers))
        dish = model.restaurant.waiting_dishes[0]

        if cookers:
            cooker = cookers[0]
            cooker.cook(model, dish)

    def __init__(self, dish):
        self.dish = dish


class CookerFreeEvent:
    def __init__(self, cooker, dish):
        self.cooker = cooker
        self.dish = dish

    def handle(self, model):
        waiting_dishes = model.restaurant.waiting_dishes
        self.cooker.available = True
        logging.info("%s: Cooker %d finished cooking dish %d for request %d",
                     human_readable_time(model.global_time), self.cooker.id, self.dish.id, self.dish.request.id)

        if waiting_dishes:
            self.cooker.cook(model, waiting_dishes[0])


class DishEvent:
    def handle(self, model):
        waiters = list(filter(lambda wait: wait.state == WaiterState.FREE, model.restaurant.waiters))
        model.restaurant.ready_dishes.append(self.dish)

        if waiters:
            waiter = waiters[0]
            waiter.deliver(model, self.dish)
        else:
            logging.info("%s: No free waiter for cooker %d  and dish %d for request %d",
                         human_readable_time(model.global_time), self.cooker.id, self.dish.id, self.dish.request.id)

        model.next_events.append(Event(model.global_time, CookerFreeEvent(self.cooker, self.dish)))

    def __init__(self, dish, cooker):
        self.dish = dish
        self.cooker = cooker
