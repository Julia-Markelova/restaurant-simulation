"""
There are request's events which will be done in the future at their time.
Events are saved in a list with their starting time and a handle function.
Requests are generated until last_entrance_time
"""

from random import expovariate, choices
from events import waiter_event as w, event as e
from restaurant import Request
from states import RequestState, WaiterState
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


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
                     model.human_time(), self.request.id, self.dish.id, self.request.dish_count)

        # to fix a bug with negative dishes
        if self.request.dish_count < 1:
            self.request.dish_count = 0
            waiters = list(filter(lambda wait: wait.state == WaiterState.FREE, model.restaurant.waiters))
            reorder = choices([False, True],
                              [1 - self.request.reorder_probability, self.request.reorder_probability])[0]

            if reorder:
                self.request.state = RequestState.WAITING_FOR_WAITER
                logging.info("%s: Request %d will make a reorder.", model.human_time(), self.request.id)
                model.reordered += 1
                if waiters:
                    waiter = waiters[0]
                    logging.info("%s: Waiter %d is taking a reorder of request %d.",
                                 model.human_time(), waiter.id, self.request.id)
                    w.waiter_service(waiter, model, self.request)

            else:
                self.request.state = RequestState.WAITING_FOR_BILL
                logging.info("%s: Request %d is going to leave.", model.human_time(), self.request.id)
                if waiters:
                    waiter = waiters[0]
                    w.bill_service(model, waiter)

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
        self.request.table.available = True
        self.request.table.owner = None

        if self.request.state == RequestState.WAITING_FOR_WAITER:
            model.bad_leave_counter += 1
            logging.info("%s: Request %d left because of too long waiting",
                         model.human_time(), self.request.id)
        else:
            model.dislike_menu += 1
            logging.info("%s: Request %d left because of disliking a menu",
                         model.human_time(), self.request.id)

    def __init__(self, request):
        self.request = request


class RequestEvent:
    def handle(self, model):
        """
        Generating new request (exponential with custom meaning) with N people.
        Take a table and waiting for the waiter.
        If there are no free table, request is going to leave.
        Increment counter of visitors or lost.
        :param model: current state of model
        """
        model.all += 1
        # trying to seize table
        tables = list(filter(lambda t: t.size >= self.request.size and t.available, model.restaurant.tables))
        logging.info("%s: Income request %d", model.human_time(), self.request.id)

        if tables:
            self.request.table = tables[0]
            self.request.table.available = False
            self.request.table.owner = self.request
            model.seated_count += 1
            logging.info("%s: Request %d took a table %d",
                         model.human_time(), self.request.id, self.request.table.id)
            # here we have some time to read a menu and make a decision about state here or not
            leaving = choices([False, True],
                              [1 - model.restaurant.leaving_probability,
                               model.restaurant.leaving_probability])[0]

            if leaving:
                model.next_events.append(
                    e.Event(model.global_time + round(expovariate(1 / model.restaurant.thinking_time)),
                            LeaveEvent(self.request))
                )

            else:
                model.next_events.append(
                    e.Event(model.global_time + round(expovariate(1 / model.restaurant.thinking_time)),
                            w.WaiterEvent(self.request)))
        else:
            model.lost_counter += 1

        people_count = int(choices(list(model.class_probability.keys()),
                                   list(model.class_probability.values()))[0])

        """
        Generating next event in seconds according to current_mean and until last_entrance_time.
        Increment counter of requests
        """
        if model.global_time < model.restaurant.last_entrance_time:
            next_request_time = round(expovariate(1 / model.current_request_mean()))
            model.next_events.append(e.Event(model.global_time + next_request_time,
                                             RequestEvent(Request(people_count,
                                                                  model.restaurant.reorder_probability))))

    def __init__(self, request):
        self.request = request
        # eating_time?
