from functools import reduce
from collections import defaultdict

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

avg_waiting_queue = defaultdict(int)
avg_dishes_queue = defaultdict(int)
avg_billing_queue = defaultdict(int)

long_waiting_leave_counter = 0
serviced_counter = 0
seated_counter = 0
no_seat_counter = 0
reorder_counter = 0
disliked_menu_counter = 0
total_counter = 0


def avg_time(stay_time):
    """
    Calculate average value of given list of times and returns value in human readable format.
    :param stay_time: list of time values
    :return: average time in human readable format
    """
    if stay_time:
        return human_readable_time(count_avg(stay_time, 0))
    else:
        return 0


def count_avg(list_of_values, scale):
    """
    Calculate average value of given list with given scale
    :param list_of_values: some list if int
    :param scale: int to round average meaning
    :return: average value
    """
    if list_of_values:
        avg = reduce(lambda x, y: x + y, list_of_values) / len(list_of_values)

        if scale > 0:
            return round(avg, scale)
        else:
            return round(avg)
    else:
        return 0


def worker_periods_loads(work_hours, close_time):
    """
    Calculate load in each interval.
    If load > 1 it will replaced with 1.
    :param work_hours: map with intervals and working time in seconds
    :param close_time: model global time to calculate load in the last interval correctly
    :return: a list with values of load
    """
    list_ = [round(v / (k.toInterval - k.fromInterval), 3) if not k.last
             else round(v / (close_time - k.fromInterval), 3)
             for k, v in work_hours.items()]
    for index, item in enumerate(list_):
        if item > 1:
            list_[index] = 1
    return list_


def count_sum(list_of_values):
    """
    Count sum of a given list of values
    :param list_of_values: some list of values
    :return: sum
    """
    if list_of_values:
        return reduce(lambda x, y: x + y, list_of_values)


def avg_waiting_time(waiting_times):
    """
    Count average waiting time.
    :param waiting_times: list of waiting times in seconds
    :return: average human readable time of waiting
    """
    times = [value for key, value in waiting_times.items() if value != 0]
    return human_readable_time(count_avg(times, 0))


def multi_period_worker_load(worker_hours, close_time):
    """
    Calculate worker's load in each interval.
    :param worker_hours: map {id {interval obj: working time in seconds}}
    :param close_time: model global time to calculate load in last interval correct
    :return: map {id {interval obj: load }}
    """
    return {k: worker_periods_loads(v, close_time) for k, v in worker_hours.items()}


def total_worker_load(worker_id, worker_hours, close_time):
    """
    Calculate load in all time restaurant works.
    :param worker_id: id for current worker
    :param worker_hours: map {id {interval obj: working seconds}}
    :param close_time: model global time to calculate total load correctly
    :return: load value if value < 1 else 1
    """
    period_load = worker_hours[worker_id]

    sum_seconds = reduce(lambda a, b: a + b, period_load.values())
    sum_keys = 0

    for key in period_load:
        sum_keys += (key.toInterval - key.fromInterval) if not key.last \
            else close_time - key.fromInterval

    return round(sum_seconds / sum_keys, 3) if round(sum_seconds / sum_keys, 3) < 1 else 1


# TODO: Yakov, think about it
# ВОЗМОЖНО ЗДЕСЬ ГОВНО
def avg_len_dict(a_dict, total):
    a_list = [key * value / total for key, value in a_dict.items()]
    return round(reduce(lambda a, b: a + b, a_list), 6)

# TODO: replace dict with defaultdict
# TODO: give normal names to all this shit
# TODO: stddev, export xls
