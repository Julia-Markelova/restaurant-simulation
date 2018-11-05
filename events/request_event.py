"""
There are request's events which will be done in the future at their time.
Events are saved in a list with their starting time and a handle function.
"""

from random import expovariate, choices
from events import waiter_event as w, event as e
from restaurant import Request
from states import State
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


class EatingFinishEvent:
    def handle(self, model):
        waiters = list(filter(lambda wait: wait.available, model.restaurant.waiters))
        self.request.status = State.WAITING_FOR_BILL

        if waiters:
            waiter = waiters[0]
            w.bill_service(model, waiter)

    def __init__(self, request):
        self.request = request


class LeaveEvent:
    """
    If request is waiting more then N minutes, we will lost it
    """

    def handle(self, model):
        if self.request.status == State.WAITING_FOR_WAITER:
            self.request.table.available = True
            self.request.table.owner = None
            model.bad_leave_counter += 1
            logging.info("%s: Request %d left because of too long waiting", model.human_time(), self.request.id)

    def __init__(self, request):
        self.request = request


class RequestEvent:
    """
    Generating new request (exponential with custom meaning).
    Take a table and waiting for the waiter.
    """

    def handle(self, model):
        # trying to seize table
        tables = list(filter(lambda t: t.size >= self.request.size and t.available, model.restaurant.tables))
        logging.info("%s: Income request %d", model.human_time(), self.request.id)

        if tables:
            self.request.table = tables[0]
            self.request.table.available = False
            self.request.table.owner = self.request
            model.count += 1
            logging.info("%s: Take a table %d request %d",
                         model.human_time(), self.request.table.id, self.request.id)
            # here we have some time to read a menu before calling a waiter
            model.next_events.append(e.Event(model.global_time + round(expovariate(1 / 300)),
                                             w.WaiterEvent(self.request)))
        else:
            model.lost_counter += 1

        people_count = int(choices(list(model.class_probability.keys()),
                                   list(model.class_probability.values()))[0])

        """
        Generating next event in seconds according to current_mean.
        Increment counter of requests
        """
        next_request_time = round(expovariate(1 / model.current_request_mean()))
        model.next_events.append(e.Event(model.global_time + next_request_time,
                                         RequestEvent(Request(people_count))))
        model.all += 1

    def __init__(self, request):
        self.request = request
        # eating_time?
