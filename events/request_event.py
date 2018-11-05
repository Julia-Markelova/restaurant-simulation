"""
There are request's events which will be done in the future at their time.
Events are saved in a list with their starting time and a handle function.
"""

from random import expovariate, choices
from events import waiter_event as w, event
from restaurant import Request
from states import State


class EatingFinishEvent:
    def handle(self, model):
        # TODO: asking for a bill or for extra dish
        self.req.table.available = True

    def __init__(self, req):
        self.req = req


class LeaveEvent:
    """
    If request is waiting more then N minutes, we will lost it
    """

    def handle(self, model):
        if self.request.status == State.WAITING:
            self.request.table.available = True
            model.lost_counter += 1

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

        if tables:
            self.request.table = tables[0]
            self.request.table.available = False
            self.request.table.owner = self.request
            model.count += 1
            # here we have some time to read a menu before calling a waiter
            model.next_events.append(event.Event(model.global_time + expovariate(1 / 300),
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
        model.next_events.append(event.Event(model.global_time + next_request_time,
                                             RequestEvent(Request(people_count))))

    def __init__(self, request):
        self.request = request
        # eating_time?
