from functools import reduce

stay_times_normal_leave = []
stay_times_bad_menu_leave = []
stay_times_long_waiting_leave = []

cook_time = []
service_time = []
delivery_time = []
dish_counter = []

cooker_hours = {}
waiter_hours = {}


long_waiting_leave_counter = 0
serviced_counter = 0
seated_counter = 0
no_seat_counter = 0
reorder_counter = 0
disliked_menu_counter = 0
total_counter = 0


def avg_stay_time(stay_time):
    if stay_time:
        return reduce(lambda x, y: x + y, stay_time) / len(stay_time)
    else:
        return 0


def worker_load(work_hours, day_len):
    if work_hours:
        return {k: v / day_len for k, v in work_hours.items()}
# TODO: closing strategy
# TODO: round delete
# TODO: events in time interval
# TODO: wtf with waiters and cookers count???
