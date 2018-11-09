from functools import reduce

from restaurant_simulation.utils import human_readable_time

stay_times_normal_leave = []
stay_times_bad_menu_leave = []
stay_times_long_waiting_leave = []

cook_time = []
service_time = []
delivery_time = []
dish_counter = []
billed_dish_counter = []

cooker_hours = {}
waiter_hours = {}
request_waiting = {}

long_waiting_leave_counter = 0
serviced_counter = 0
seated_counter = 0
no_seat_counter = 0
reorder_counter = 0
disliked_menu_counter = 0
total_counter = 0


def avg_time(stay_time):
    if stay_time:
        return human_readable_time(count_avg(stay_time, 0))
    else:
        return 0


def count_avg(list_of_values, scale):
    if list_of_values:
        avg = reduce(lambda x, y: x + y, list_of_values) / len(list_of_values)

        if scale > 0:
            return round(avg, scale)
        else:
            return round(avg)
    else:
        return 0


def worker_periods_loads(work_hours):
    if work_hours:
        return [round(v / (k.toInterval - k.fromInterval), 3) for k, v in work_hours.items()]


def count_sum(list_of_values):
    if list_of_values:
        return reduce(lambda x, y: x + y, list_of_values)


def avg_waiting_time(waiting_times):
    times = [value for key, value in waiting_times.items() if value != 0]
    return human_readable_time(count_avg(times, 0))


def multi_period_worker_load(worker_hours):
    return {k: worker_periods_loads(v) for k, v in worker_hours.items()}


def total_worker_load(worker_id, worker_hours):
    period_load = worker_hours[worker_id]

    sum_seconds = reduce(lambda a, b: a + b, period_load.values())
    sum_keys = 0

    for key in period_load:
        sum_keys += (key.toInterval - key.fromInterval)

    return round(sum_seconds / sum_keys, 3)