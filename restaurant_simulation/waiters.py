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
from restaurant_simulation.utils import human_readable_date_time
from restaurant_simulation.kitchen import CookerCallEvent

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


class Waiter:
    _ids = count(1)

    def service(self, model, request):
        """
        Change waiter's state to SERVICING, generate dishes for each human in request's size.
        Call CookerCallEvent for each generated dish.
        After that generate WaiterFreeEvent.
        Increase working time.
        :param self: who will work
        :param model: current state of model
        :param request:
        """
        self.state = WaiterState.SERVICING
        st.request_waiting[request.id] += model.global_time - request.waiting_start_time
        request.state = RequestState.OK  # because request already has a waiter
        logging.info("%s: Waiter %d is started servicing request %d",
                     human_readable_date_time(model.global_time),
                     self.id,
                     request.id)
        service_time = 0
        dish_count = 0

        for human in range(request.size):
            service_time += expovariate(1 / self.service_time)
            dish_count += randrange(1, 3, 1)

        request.dish_count = dish_count
        request.billed_dish_counter += dish_count
        st.dish_counter.append(dish_count)

        logging.info("%s: Request %d ordered %d dishes",
                     human_readable_date_time(model.global_time),
                     request.id,
                     dish_count)

        for dish in range(dish_count):
            model.next_events.append(
                Event(model.global_time + service_time, CookerCallEvent(Dish(request)))
            )

        model.next_events.append(
            Event(model.global_time + service_time, WaiterFreeEvent(self, request)))

        st.service_time.append(round(service_time))
        st.waiter_hours[self.id][model.current_request_interval()] += round(service_time)

        request.waiting_start_time = model.global_time + service_time

    def deliver(self, model, dish):
        """
        Change waiter's state to DELIVER.
        Remove ready dish from dish queue.
        Calculate request's waiting time.
        Append WaiterFree and EatingFinish events.
        :param model: current state of model
        :param dish: dish obj to know for whom deliver
        """
        self.state = WaiterState.DELIVERING_DISH
        model.restaurant.ready_dishes.remove(dish)
        delivery_time = expovariate(1 / model.restaurant.delivery_time)  # time to deliver food
        st.delivery_time.append(delivery_time)

        st.waiter_hours[self.id][model.current_request_interval()] += round(delivery_time)

        model.next_events.append(Event(model.global_time + delivery_time,
                                       WaiterFreeEvent(self, dish.request, dish)))

        if dish.request.state != RequestState.EATING:
            st.request_waiting[dish.request.id] += \
                model.global_time + delivery_time - dish.request.waiting_start_time

        dish.request.state = RequestState.EATING
        model.next_events.append(
            Event(
                model.global_time + delivery_time + expovariate(1 / model.restaurant.eating_time),
                vis.EatingFinishEvent(dish)
            )
        )

    def invoice(self, model):
        """
        Check if somebody is waiting for a bill.
        If somebody is waiting, waiter change state to BILLINg and request's state to OK.
        Increase working hours.
        Call WaiterFree and TableFree events.
        :param model: current state of model
        """
        waiting_for_bill = list(
            map(
                lambda t: t.owner,
                filter(
                    lambda table: not table.available and table.owner.state == RequestState.WAITING_FOR_BILL,
                    model.restaurant.tables
                )
            )
        )

        if waiting_for_bill:
            self.state = WaiterState.BILLING
            leaving = waiting_for_bill[0]
            st.request_waiting[leaving.id] += model.global_time - leaving.waiting_start_time
            logging.info("%s: Request %d is billing by waiter %d",
                         human_readable_date_time(model.global_time),
                         leaving.id, self.id)
            leaving.state = RequestState.OK
            service_time = expovariate(1 / self.service_time)
            st.service_time.append(service_time)
            st.waiter_hours[self.id][model.current_request_interval()] += round(service_time)

            model.next_events.append(Event(model.global_time + service_time,
                                           WaiterFreeEvent(self, leaving)))
            model.next_events.append(Event(model.global_time + service_time,
                                           TableFreeEvent(leaving.table)))

    def __init__(self, service_time, intervals):
        """
        Constructor for waiters in a restaurant_simulation
        :param service_time: average time to take an order
        """
        self.service_time = service_time
        self.id = next(self._ids)
        self.state = WaiterState.FREE
        st.waiter_hours[self.id] = {}

        for interval in intervals:
            st.waiter_hours[self.id][interval] = 0


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
                Event(model.global_time + expovariate(1 / model.restaurant.waiting_time),
                      vis.LeaveEvent(self.request)))

    def __init__(self, request):
        self.request = request


class WaiterFreeEvent:

    def handle(self, model):
        """
        Check if there are ready dishes, if not check if there are requests waiting for waiter,
        if not check if there requests waiting for bill, if not become free.
        :param model: current state of model
        """

        if self.waiter.state == WaiterState.DELIVERING_DISH:
            logging.info("%s: Waiter %d delivered dish %d to request %d",
                         human_readable_date_time(model.global_time),
                         self.waiter.id, self.dish.id, self.request.id)
        elif self.waiter.state == WaiterState.BILLING:
            logging.info("%s: Waiter %d finished billing request %d",
                         human_readable_date_time(model.global_time),
                         self.waiter.id, self.request.id)
        elif self.waiter.state == WaiterState.SERVICING:
            logging.info("%s: Waiter %d finished servicing request %d",
                         human_readable_date_time(model.global_time),
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
        """
        Billed dishes counter increased.
        Serviced counter incremented.
        Stay times calculated.
        Free table.
        :param model: current state of model
        """
        logging.info("%s: Request %d is leaving table %d",
                     human_readable_date_time(model.global_time),
                     self.table.owner.id,
                     self.table.id)
        st.billed_dish_counter.append(self.table.owner.billed_dish_counter)
        st.serviced_counter += 1
        st.stay_times_normal_leave.append(model.global_time - self.table.owner.income_time)
        self.table.available = True
        self.table.owner = None
