"""
There are different types of events which will be done in the future at their time.
Events are saved in a list with their starting time and a handle function.
"""

from random import expovariate, choices, randrange

from restaurant import Request
from states import State


def waiter_service(waiter, model, request):
    waiter.available = False
    delay = 0
    dish_count = 0

    for human in range(request.size):
        delay += expovariate(1 / waiter.service_time)
        dish_count += randrange(0, 3, 1)

    for dish in range(dish_count):
        pass
    # TODO: implement CookerCallEvent
    #        model.next_events.append(
    #            Event(
    #                model.global_time + delay + expovariate(1 / model.cooking_time),
    #                DishEvent(request)
    #            )
    #        )

    model.next_events.append(Event(model.global_time + delay, WaiterFreeEvent(waiter)))


class Event:
    def handle(self, model):
        self.what.handle(model)

    def __init__(self, when, what):
        self.when = when
        self.what = what


class DishEvent:
    # TODO: write any logic about cookers
    def handle(self, model):
        pass

    def __init__(self, request):
        self.request = request


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
            model.next_events.append(Event(model.global_time + expovariate(1 / 600),
                                           LeaveEvent(self.request)))

    def __init__(self, request):
        self.request = request


class EatingFinishEvent:
    def handle(self, model):
        # TODO: asking for a bill or for extra dish
        self.req.table.available = True

    def __init__(self, req):
        self.req = req


class WaiterFreeEvent:

    def handle(self, model):
        self.waiter.available = True
        dishes = list(filter(lambda d: d.is_ready, model.restaurant.dishes))

        if dishes:
            self.waiter.available = False
            dish = dishes[0]
            delay = expovariate(1 / 300)
            model.restaurant.dishes.remove(dish)
            model.next_events.append(Event(model.global_time + delay, WaiterFreeEvent(self.waiter)))
            model.next_events.append(
                Event(
                    model.global_time + delay + expovariate(1 / model.restaurant.eating_time),
                    EatingFinishEvent(dish.request)
                )
            )

        else:
            tables = list(filter(lambda t: not t.available and t.owner.status == State.WAITING,
                                 model.restaurant.tables))

            if tables:
                request = tables[0].owner
                waiter_service(self.waiter, model, request)

    def __init__(self, waiter):
        self.waiter = waiter


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
            model.next_events.append(Event(model.global_time + expovariate(1 / 300),
                                           WaiterEvent(self.request)))
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
                                       RequestEvent(Request(people_count))))

    def __init__(self, request):
        self.request = request
        # eating_time?
