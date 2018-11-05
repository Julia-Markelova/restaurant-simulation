"""
Cooker's logic is here.
"""


from random import expovariate
from events import event


class CookerCallEvent:
    def __init__(self, dish):
        self.dish = dish

    def handle(self, model):
        model.restaurant.waiting_dishes.append(self.dish)
        cookers = list(filter(lambda c: c.available, model.restaurant.cookers))
        dish = model.restaurant.waiting_dishes[0]

        if cookers:
            cooker = cookers[0]
            cooker_service(cooker, model, dish)


def cooker_service(cooker, model, dish):
    cooker.available = False
    cooking_time = expovariate(1 / cooker.cooking_time)
    model.restaurant.waiting_dishes.remove(dish)
    model.next_events.append(event.Event(model.global_time + cooking_time, DishEvent(dish, cooker)))


class CookerFreeEvent:
    def __init__(self, cooker):
        self.cooker = cooker

    def handle(self, model):
        waiting_dishes = model.restaurant.waiting_dishes
        self.cooker.available = True

        if waiting_dishes:
            cooker_service(self.cooker, model, waiting_dishes[0])


class DishEvent:
    def handle(self, model):
        model.restaurant.ready_dishes.append(self.dish)
        model.next_events.append(event.Event(model.global_time, CookerFreeEvent(self.cooker)))

    def __init__(self, dish, cooker):
        self.dish = dish
        self.cooker = cooker
