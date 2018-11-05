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
    logging.info("%s: Waiter %d is started servicing request %d", model.human_time(), waiter.id, request.id)
    service_time = 0
    dish_count = 0

    for human in range(request.size):
        service_time += expovariate(1 / waiter.service_time)
        dish_count += randrange(0, 3, 1)

    request.dish_count = dish_count

    for dish in range(dish_count):
        model.next_events.append(
            event.Event(model.global_time + round(service_time), cooker_event.CookerCallEvent(Dish(request)))
        )

    model.next_events.append(
        event.Event(model.global_time + round(service_time), WaiterFreeEvent(waiter, request)))


def delivery_service(waiter, model, dish):
    model.restaurant.ready_dishes.remove(dish)
    delivery_time = expovariate(1 / model.restaurant.delivery_time)  # time to deliver food
    model.next_events.append(event.Event(model.global_time + round(delivery_time),
                                         WaiterFreeEvent(waiter, dish.request)))
    dish.request.dish_count -= 1
    logging.info("%s: Dish %d is delivered to request %d, remain dishes: %d",
                 model.human_time(), dish.id, dish.request.id, dish.request.dish_count)
    if dish.request.dish_count < 1:
        model.next_events.append(
            event.Event(
                model.global_time + round(delivery_time + expovariate(1 / model.restaurant.eating_time)),
                r.EatingFinishEvent(dish.request)
            )
        )


def bill_service(model, waiter):
    waiting_for_bill = list(
        map(lambda t: t.owner,
            filter(lambda table: table.owner is not None and table.owner.status == State.WAITING_FOR_BILL,
                   model.restaurant.tables
                   )
            )
    )

    if waiting_for_bill:
        waiter.available = False
        leaving = waiting_for_bill[0]
        logging.info("%s: Request %d is billing by waiter %d", model.human_time(),
                     leaving.id, waiter.id)
        leaving.status = State.OK
        service_time = expovariate(1 / waiter.service_time)
        model.next_events.append(event.Event(model.global_time + round(service_time),
                                             TableFreeEvent(leaving.table)))
        model.next_events.append(event.Event(model.global_time + round(service_time),
                                             WaiterFreeEvent(waiter, leaving)))


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
            self.request.status = State.WAITING_FOR_WAITER
            model.next_events.append(
                event.Event(model.global_time + round(expovariate(1 / model.restaurant.waiting_time)),
                            r.LeaveEvent(self.request)))

    def __init__(self, request):
        self.request = request


class WaiterFreeEvent:

    def handle(self, model):
        self.waiter.available = True
        logging.info("%s: Waiter %d is finished servicing request %d", model.human_time(),
                     self.waiter.id, self.request.id)
        dishes = list(filter(lambda d: d.is_ready, model.restaurant.ready_dishes))

        if dishes:
            self.waiter.available = False
            dish = dishes[0]
            delivery_service(self.waiter, model, dish)

        else:
            tables = list(filter(lambda t: not t.available and t.owner.status == State.WAITING_FOR_WAITER,
                                 model.restaurant.tables))

            if tables:
                request = tables[0].owner
                waiter_service(self.waiter, model, request)

            else:
                bill_service(model, self.waiter)

    def __init__(self, waiter, request):
        self.waiter = waiter
        self.request = request


class TableFreeEvent:
    def __init__(self, table):
        self.table = table

    def handle(self, model):
        logging.info("%s: Request %d is leaving table %d",
                     model.human_time(),
                     self.table.owner.id,
                     self.table.id)
        model.serviced += 1
        self.table.available = True
        self.table.owner = None
