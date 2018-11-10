"""
There are request's events which will be done in the future at their time.
Events are saved in a list with their starting time and a handle function.
Requests are generated until last_entrance_time
"""

import logging
import sys
from itertools import count
from random import expovariate, choices

import restaurant_simulation.event as e
import restaurant_simulation.stats as st
import restaurant_simulation.waiters as w
from restaurant_simulation.states import RequestState, WaiterState
from restaurant_simulation.utils import human_readable_date_time

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


class Request:
    _ids = count(1)

    def __init__(self, size, reorder_probability, income_time):
        """
        Constructor for request
        table: which table request is chosen
        dish_count: count of ordered dishes
        :param size: how many people are coming
        :param reorder_probability: float describing probability of on more order
        :param income_time: int, time of request's creating
        """
        self.id = next(self._ids)
        self.waiting_start_time = 0
        st.request_waiting[self.id] = 0
        self.size = size
        self.table = None
        self.state = RequestState.OK
        self.dish_count = 0
        self.billed_dish_counter = 0
        self.reorder_probability = reorder_probability
        self.income_time = income_time
        self.reorder = False


class EatingFinishEvent:
    def handle(self, model):
        """
        Delivered dishes decremented (ate).
        If there are no dish we wait, we will call a waiter for an extra order with reorder_probability.
        On the other way, request will call a waiter for a bill.
        If there are no waiter we will wait while he comes.
        :param model: current state of model
        """
        self.request.dish_count -= 1
        self.request.state = RequestState.OK
        logging.info("%s: Request %d ate a dish %d. Remaining dishes: %d",
                     human_readable_date_time(model.global_time),
                     self.request.id,
                     self.dish.id,
                     self.request.dish_count)

        # to fix a bug with negative dishes
        if self.request.dish_count < 1:
            self.request.dish_count = 0
            waiters = list(filter(lambda wait: wait.state == WaiterState.FREE, model.restaurant.waiters))
            reorder = choices([False, True],
                              [1 - self.request.reorder_probability, self.request.reorder_probability])[0]

            self.request.waiting_start_time = model.global_time

            if reorder and model.global_time <= model.restaurant.last_entrance_time:
                self.request.state = RequestState.WAITING_FOR_WAITER
                logging.info("%s: Request %d will make a reorder.",
                             human_readable_date_time(model.global_time),
                             self.request.id)

                if not self.request.reorder:
                    st.reorder_counter += 1

                self.request.reorder = True

                if waiters:
                    waiter = waiters[0]
                    logging.info("%s: Waiter %d is taking a reorder of request %d.",
                                 human_readable_date_time(model.global_time),
                                 waiter.id,
                                 self.request.id)
                    waiter.service(model, self.request)

            else:
                self.request.state = RequestState.WAITING_FOR_BILL
                logging.info("%s: Request %d is going to leave.",
                             human_readable_date_time(model.global_time),
                             self.request.id)
                if waiters:
                    waiter = waiters[0]
                    waiter.invoice(model)

            self.request.reorder_probability *= 0.5

    def __init__(self, dish):
        self.request = dish.request
        self.dish = dish


class LeaveEvent:
    def handle(self, model):
        """
        If request is waiting more then N minutes or request does not like a menu, we will lost it
        When request is leaving, it makes its table free
        :param model: current state of model
        """

        if self.request.state == RequestState.WAITING_FOR_WAITER or self.request.state == RequestState.LEAVING_BAD_MENU:
            self.request.table.available = True
            self.request.table.owner = None

            if self.request.state == RequestState.WAITING_FOR_WAITER:
                st.stay_times_long_waiting_leave.append(model.global_time - self.request.income_time)
                st.long_waiting_leave_counter += 1
                logging.info("%s: Request %d left because of too long waiting",
                             human_readable_date_time(model.global_time), self.request.id)
            elif self.request.state == RequestState.LEAVING_BAD_MENU:
                st.stay_times_bad_menu_leave.append(model.global_time - self.request.income_time)
                st.disliked_menu_counter += 1
                logging.info("%s: Request %d left because of disliking a menu",
                             human_readable_date_time(model.global_time), self.request.id)

    def __init__(self, request):
        self.request = request


class RequestEvent:
    def handle(self, model):
        """
        Generating new request (exponential with custom meaning) with N people.
        Take a table and waiting for the waiter or check menu and leave with leaving probability.
        If there are no free table, request is going to leave.
        Increment counter of visitors or lost.
        :param model: current state of model
        """
        st.total_counter += 1
        # trying to seize table
        tables = list(filter(lambda t: t.size >= self.request.size and t.available, model.restaurant.tables))
        logging.info("%s: Income request %d", human_readable_date_time(model.global_time), self.request.id)

        if tables:
            self.request.table = tables[0]
            self.request.table.available = False
            self.request.table.owner = self.request
            st.seated_counter += 1

            logging.info("%s: Request %d took a table %d",
                         human_readable_date_time(model.global_time), self.request.id, self.request.table.id)
            # here we have some time to read a menu and make a decision about state here or not
            leaving = choices([False, True],
                              [1 - model.restaurant.leaving_probability,
                               model.restaurant.leaving_probability])[0]

            if leaving:
                self.request.state = RequestState.LEAVING_BAD_MENU
                model.next_events.append(
                    e.Event(model.global_time + expovariate(1 / model.restaurant.thinking_time),
                            LeaveEvent(self.request))
                )

            else:
                self.request.waiting_start_time = model.global_time
                model.next_events.append(
                    e.Event(model.global_time + expovariate(1 / model.restaurant.thinking_time),
                            w.WaiterEvent(self.request)))
        else:
            st.no_seat_counter += 1
            logging.info("%s: Request %d left because there are not free table",
                         human_readable_date_time(model.global_time), self.request.id)

        people_count = int(choices(list(model.class_probability.keys()),
                                   list(model.class_probability.values()))[0])

        """
        Generating next event in seconds according to current_mean and until last_entrance_time.
        Increment counter of requests
        """
        next_request_time = expovariate(1 / model.current_request_mean())

        if model.global_time < model.restaurant.last_entrance_time \
                and model.request_interval(model.global_time + next_request_time).interval != 0:
            model.next_events.append(e.Event(model.global_time + next_request_time,
                                             RequestEvent(Request(people_count,
                                                                  model.restaurant.reorder_probability,
                                                                  model.global_time + next_request_time))))

    def __init__(self, request):
        self.request = request
        # eating_time?
