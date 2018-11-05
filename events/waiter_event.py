"""
Waiter's logic is here.
"""

from events import cooker_event, event, request_event as r
from random import expovariate, randrange
from states import State
from restaurant import Dish
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


def waiter_service(waiter, model, request):
    waiter.available = False
    logging.info("%s: Water started service request number %d", model.human_time(), request.req_id)
    service_time = 0
    dish_count = 0

    for human in range(request.size):
        service_time += expovariate(1 / waiter.service_time)
        dish_count += randrange(0, 3, 1)

    request.dish_count = dish_count

    for dish in range(dish_count):
        model.next_events.append(
            event.Event(model.global_time + service_time, cooker_event.CookerCallEvent(Dish(request)))
        )

    model.next_events.append(event.Event(model.global_time + service_time, WaiterFreeEvent(waiter, request)))


def delivery_service(waiter, model, dish):
    delivery_time = expovariate(1 / 300)  # time to deliver food
    model.restaurant.ready_dishes.remove(dish)
    model.next_events.append(event.Event(model.global_time + delivery_time,
                                         WaiterFreeEvent(waiter, dish.request)))
    dish.request.dish_count -= 1
    logging.info("%s: Dish is delivered to request number %d, remain dishes: %d",
                 model.human_time(), dish.request.req_id, dish.request.dish_count)
    if dish.request.dish_count == 0:
        model.next_events.append(
            event.Event(
                model.global_time + delivery_time + expovariate(1 / model.restaurant.eating_time),
                r.EatingFinishEvent(dish.request)
            )
        )


def bill_service(model, waiter):
    bills = model.restaurant.bill

    if bills:
        waiter.available = False
        request = bills[0]
        logging.info("%s: Waiter started billed request number %d", model.human_time(), request.req_id)
        bills.remove(request)
        service_time = expovariate(1 / waiter.service_time)
        model.next_events.append(event.Event(model.global_time + service_time,
                                             TableFreeEvent(request.table)))
        model.next_events.append(event.Event(model.global_time + service_time,
                                             WaiterFreeEvent(waiter, request)))


class WaiterEvent:
    """
    Check for free waiter and seize them.
    Calculate delay-time and generate dishes.
    If there is no free waiters, people will wait for N minutes.
    If nobody is coming, person will leave the restaurant.
    """

    def handle(self, model):
        waiters = list(filter(lambda w: w.available, model.restaurant.waiters))

        if waiters:
            waiter = waiters[0]
            waiter_service(waiter, model, self.request)

        else:
            self.request.state = State.WAITING
            waiting_time = 600  # wait 600s before leave the restaurant
            model.next_events.append(event.Event(model.global_time + expovariate(1 / waiting_time),
                                                 r.LeaveEvent(self.request)))

    def __init__(self, request):
        self.request = request


class WaiterFreeEvent:

    def handle(self, model):
        self.waiter.available = True
        logging.info("%s: Waiter finished service request number %d", model.human_time(), self.req.req_id)
        dishes = list(filter(lambda d: d.is_ready, model.restaurant.ready_dishes))

        if dishes:
            self.waiter.available = False
            dish = dishes[0]
            delivery_service(self.waiter, model, dish)

        else:
            tables = list(filter(lambda t: not t.available and t.owner.status == State.WAITING,
                                 model.restaurant.tables))

            if tables:
                request = tables[0].owner
                waiter_service(self.waiter, model, request)

            else:
                bill_service(model, self.waiter)

    def __init__(self, waiter, req):
        self.waiter = waiter
        self.req = req


class TableFreeEvent:
    def __init__(self, table):
        self.table = table

    def handle(self, model):
        logging.info("%s: Leave request number %d", model.human_time(), self.table.owner.req_id)
        model.serviced += 1
        self.table.available = True
        self.table.owner = None
