from random import expovariate, choices
from generating import Event


class Table:
    def __init__(self, size):
        self.size = size
        self.available = True


class Waiter:
    def __init__(self, service_time):
        self.service_time = service_time
        self.available = True


class Cooker:
    def __init__(self, cooking_time):
        self.cooking_time = cooking_time


class WaiterCall:

    def handle(self, model):
        pass

    def __init__(self, request):
        self.request = request


class Request:
    """
    Generating new request (exponential with custom meaning).
    Take a table and waiting for the waiter.
    """

    def handle(self, model):
        # trying to seize table
        tables = list(filter(lambda t: t.size >= self.size and t.available, model.tables))

        if tables:
            table = tables[0]
            table.available = False
            # model.next_events.append(Event(model.global_time + expovariate(1 / 300), WaiterCall(self)))
        else:
            pass
            # TODO: implement lost counter

        people_count = int(choices(list(model.class_probability.keys()),
                                   list(model.class_probability.values()))[0])

        """
        Generating next event in seconds according to current_mean.
        Increment counter of requests
        """
        next_request_time = round(expovariate(1 / model.current_request_mean()))
        model.next_events.append(Event(model.global_time + next_request_time, Request(people_count)))
        model.count += 1

    def __init__(self, size):
        self.size = size
        # eating_time?
