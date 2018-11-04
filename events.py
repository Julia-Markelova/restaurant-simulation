"""
There are different types of events which will be done in the future at their time.
Events are saved in a list with their starting time and a handle function.
"""

from random import expovariate, choices, randrange


class Event:
    def handle(self, model):
        self.what.handle(model)

    def __init__(self, when, what):
        self.when = when
        self.what = what


class DishEvent:
    def handle(self, model):
        pass

    def __init__(self, request):
        self.request = request


class WaiterEvent:
    """
    Check for free waiter and seize them.
    Calculate delay-time and generate dishes.
    If there is no free waiters, people will be waiting more or leave the restaurant.
    Probability of leaving is growing each time human wait.
    """

    def handle(self, model):
        waiters = list(filter(lambda w: w.available, model.waiters))

        if waiters:
            waiter = waiters[0]
            waiter.available = False
            delay = 0
            dish_count = 0

            for human in range(self.request.size):
                delay += expovariate(1 / waiter.service_time)
                dish_count += randrange(0, 3, 1)

            for dish in range(dish_count):
                model.next_events.append(
                    Event(
                        model.global_time + delay + expovariate(1 / model.cooking_time),
                        DishEvent(self.request)
                    )
                )

            model.next_events.append(model.global_time + delay, WaiterFreeEvent(waiter))

        else:
            pass
            #  TODO: doing sth if no free waiters

    def __init__(self, request):
        self.request = request


class WaiterFreeEvent:

    def handle(self, model):
        self.waiter.available = True
        # TODO: check kitchen, check tables

    def __init__(self, waiter):
        self.waiter = waiter


class RequestEvent:
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
            model.count += 1
            # here we have some time to read a menu before calling a waiter
            model.next_events.append(Event(model.global_time + expovariate(1 / 300),
                                           WaiterEvent(self)))
        else:
            model.lost_counter += 1

        people_count = int(choices(list(model.class_probability.keys()),
                                   list(model.class_probability.values()))[0])

        """
        Generating next event in seconds according to current_mean.
        Increment counter of requests
        """
        next_request_time = round(expovariate(1 / model.current_request_mean()))
        model.next_events.append(Event(model.global_time + next_request_time,
                                       RequestEvent(people_count)))

    def __init__(self, size):
        self.size = size
        # eating_time?

