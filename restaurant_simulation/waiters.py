"""
Waiter's logic is here.
"""

import logging
import sys
from itertools import count
from random import expovariate, randrange

import restaurant_simulation.stats as st
import restaurant_simulation.visitors as vis
from restaurant_simulation.event import Event
from restaurant_simulation.states import RequestState, WaiterState
from restaurant_simulation.utils import human_readable_time
from restaurant_simulation.kitchen import CookerCallEvent

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


class Waiter:
    _ids = count(1)

    def service(self, model, request):
        """
        Change waiter's state to SERVICING, generate dishes for each human in request's size.
        Call CookerCallEvent for each generated dish.
        After that generate WaiterFreeEvent.
        :param self: who will work
        :param model: current state of model
        :param request:
        """
        self.state = WaiterState.SERVICING
        request.state = RequestState.OK  # because request already has a waiter
        logging.info("%s: Waiter %d is started servicing request %d",
                     human_readable_time(model.global_time),
                     self.id,
                     request.id)
        service_time = 0
        dish_count = 0

        for human in range(request.size):
            service_time += expovariate(1 / self.service_time)
            dish_count += randrange(1, 3, 1)

        request.dish_count = dish_count
        logging.info("%s: Request %d ordered %d dishes",
                     human_readable_time(model.global_time),
                     request.id,
                     dish_count)

        for dish in range(dish_count):
            model.next_events.append(
                Event(model.global_time + round(service_time), CookerCallEvent(Dish(request)))
            )

        model.next_events.append(
            Event(model.global_time + round(service_time), WaiterFreeEvent(self, request)))

    def deliver(self, model, dish):
        self.state = WaiterState.DELIVERING_DISH
        model.restaurant.ready_dishes.remove(dish)
        delivery_time = expovariate(1 / model.restaurant.delivery_time)  # time to deliver food
        model.next_events.append(Event(model.global_time + round(delivery_time),
                                       WaiterFreeEvent(self, dish.request, dish)))
        model.next_events.append(
            Event(
                model.global_time + round(delivery_time + expovariate(1 / model.restaurant.eating_time)),
                vis.EatingFinishEvent(dish)
            )
        )

    def invoice(self, model):
        waiting_for_bill = list(
            map(
                lambda t: t.owner,
                filter(
                    lambda table: table.owner is not None and table.owner.state == RequestState.WAITING_FOR_BILL,
                    model.restaurant.tables
                )
            )
        )

        if waiting_for_bill:
            self.state = WaiterState.BILLING
            leaving = waiting_for_bill[0]
            logging.info("%s: Request %d is billing by waiter %d", human_readable_time(model.global_time),
                         leaving.id, self.id)
            leaving.state = RequestState.OK
            service_time = expovariate(1 / self.service_time)
            model.next_events.append(Event(model.global_time + round(service_time),
                                           WaiterFreeEvent(self, leaving)))
            model.next_events.append(Event(model.global_time + round(service_time),
                                           TableFreeEvent(leaving.table)))

    def __init__(self, service_time):
        """
        Constructor for waiters in a restaurant_simulation
        :param service_time: average time to take an order
        """
        self.service_time = service_time
        self.id = next(self._ids)
        self.state = WaiterState.FREE


class Dish:
    _ids = count(1)

    def __init__(self, request):
        """
        Constructor for a dish
        :param request: who ordered a dish
        """
        self.request = request
        self.id = next(self._ids)


class WaiterEvent:
    """
    Check for free waiter and seize them.
    Calculate delay-time and generate dishes.
    If there is no free waiters, people will wait for N minutes.
    If nobody is coming, person will leave the restaurant_simulation.
    """

    def handle(self, model):
        waiters = list(filter(lambda w: w.state == WaiterState.FREE, model.restaurant.waiters))

        if waiters:
            waiter = waiters[0]
            waiter.service(model, self.request)

        else:
            self.request.state = RequestState.WAITING_FOR_WAITER
            model.next_events.append(
                Event(model.global_time + round(expovariate(1 / model.restaurant.waiting_time)),
                      vis.LeaveEvent(self.request)))

    def __init__(self, request):
        self.request = request


class WaiterFreeEvent:

    def handle(self, model):

        if self.waiter.state == WaiterState.DELIVERING_DISH:
            logging.info("%s: Waiter %d delivered dish %d to request %d",
                         human_readable_time(model.global_time),
                         self.waiter.id, self.dish.id, self.request.id)
        elif self.waiter.state == WaiterState.BILLING:
            logging.info("%s: Waiter %d finished billing request %d",
                         human_readable_time(model.global_time),
                         self.waiter.id, self.request.id)
        elif self.waiter.state == WaiterState.SERVICING:
            logging.info("%s: Waiter %d finished servicing request %d",
                         human_readable_time(model.global_time),
                         self.waiter.id, self.request.id)

        self.waiter.state = WaiterState.FREE
        dishes = model.restaurant.ready_dishes

        if dishes:
            self.waiter.state = WaiterState.DELIVERING_DISH
            dish = dishes[0]
            self.waiter.deliver(model, dish)

        else:
            tables = list(
                filter(
                    lambda t: not t.available and t.owner.state == RequestState.WAITING_FOR_WAITER,
                    model.restaurant.tables
                )
            )

            if tables:
                request = tables[0].owner
                self.waiter.service(model, request)

            else:
                self.waiter.invoice(model)

    def __init__(self, waiter, request, dish=None):
        self.waiter = waiter
        self.request = request
        self.dish = dish


class TableFreeEvent:
    def __init__(self, table):
        self.table = table

    def handle(self, model):
        logging.info("%s: Request %d is leaving table %d",
                     human_readable_time(model.global_time),
                     self.table.owner.id,
                     self.table.id)
        st.serviced_counter += 1
        self.table.available = True
        self.table.owner = None
