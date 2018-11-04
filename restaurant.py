from random import expovariate, choices


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


class Request:
    """
    Generating new event (exponential with custom meaning).
    Event consists of time and a kind of event.
    """

    def handle(self, model):
        people_count = choices(list(model.class_probability.keys()),
                               list(model.class_probability.values()))
        # in seconds
        next_request_time = expovariate(1 / model.current_request_mean()) * 60
        model.next_events.append(model.global_time + next_request_time, Request(people_count))

        pass

    def __init__(self, size):
        self.size = size
        # eating_time?
