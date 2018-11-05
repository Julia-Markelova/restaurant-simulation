"""
Cooker's logic is here.
"""

from random import expovariate
from events import event, waiter_event as w
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


class CookerCallEvent:

    def handle(self, model):
        model.restaurant.waiting_dishes.append(self.dish)
        cookers = list(filter(lambda c: c.available, model.restaurant.cookers))
        dish = model.restaurant.waiting_dishes[0]

        if cookers:
            cooker = cookers[0]
            cooker_service(cooker, model, dish)

    def __init__(self, dish):
        self.dish = dish


def cooker_service(cooker, model, dish):
    cooker.available = False
    logging.info("%s: Cooker %d started request %d", model.human_time(),
                 cooker.id, dish.request.id)
    cooking_time = expovariate(1 / cooker.cooking_time)
    model.restaurant.waiting_dishes.remove(dish)
    model.next_events.append(event.Event(model.global_time + round(cooking_time), DishEvent(dish, cooker)))


class CookerFreeEvent:
    def __init__(self, cooker, dish):
        self.cooker = cooker
        self.dish = dish

    def handle(self, model):
        waiting_dishes = model.restaurant.waiting_dishes
        self.cooker.available = True
        logging.info("%s: Cooker %d finished request %d",
                     model.human_time(), self.cooker.id, self.dish.request.id)

        if waiting_dishes:
            cooker_service(self.cooker, model, waiting_dishes[0])


class DishEvent:
    def handle(self, model):
        waiters = list(filter(lambda wait: wait.available, model.restaurant.waiters))
        model.restaurant.ready_dishes.append(self.dish)

        if waiters:
            waiter = waiters[0]
            w.delivery_service(waiter, model, self.dish)

        model.next_events.append(event.Event(model.global_time, CookerFreeEvent(self.cooker, self.dish)))

    def __init__(self, dish, cooker):
        self.dish = dish
        self.cooker = cooker
