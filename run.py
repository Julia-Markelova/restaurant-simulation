from collections import defaultdict

import numpy as np
import scipy.stats as st
from prettytable import PrettyTable

from restaurant_simulation import model, stats, utils


def confidence_interval(values, do_round=True):
    if len(list(filter(lambda x: x != 0, values))) == 0:
        return 0, 0
    a, b = st.t.interval(0.997, len(values) - 1, loc=np.mean(values), scale=st.sem(values))

    if do_round:
        return int((a + b) / 2), int((b - a) / 2)
    else:
        return (a + b) / 2, (b - a) / 2


avg_times_normal_leave = [] #
avg_times_bad_menu_leave = [] #
avg_times_long_waiting_leave = [] #

avg_cook_time = [] #
avg_service_time = [] #
avg_delivery_time = [] #
avg_dish_count = [] #
avg_total_dish_count = [] #
avg_billed_dish_count = [] #

avg_cooker_hours = {}
avg_waiter_hours = {}
avg_request_waiting = [] #

avg_waiting_queue = [] #
avg_dishes_queue = [] #
avg_billing_queue = [] #

avg_long_waiting_leave_count = [] #
avg_serviced_count = [] #
avg_seated_count = [] #
avg_no_seat_count = [] #
avg_reorder_count = [] #
avg_disliked_menu_count = [] #
avg_total_count = [] #

for i in range(10):
    rest_model = model.Model(open('parameters.json'))
    rest_model.run()
    avg_times_normal_leave.append(stats.count_avg(stats.stay_times_normal_leave, 3))
    avg_request_waiting.append(stats.count_avg(stats.non_zero_values(stats.request_waiting), 3))
    avg_times_bad_menu_leave.append(stats.count_avg(stats.stay_times_bad_menu_leave, 3))
    avg_times_long_waiting_leave.append(stats.count_avg(stats.stay_times_long_waiting_leave, 3))
    avg_cook_time.append(stats.count_avg(stats.cook_time, 3))
    avg_service_time.append(stats.count_avg(stats.service_time, 3))
    avg_delivery_time.append(stats.count_avg(stats.delivery_time, 3))
    avg_dish_count.append(stats.count_avg(stats.dish_counter, 3))
    avg_waiting_queue.append(stats.avg_len_dict(stats.avg_waiting_queue,
                                                rest_model.restaurant.work_time_to
                                                - rest_model.restaurant.work_time_from))
    avg_dishes_queue.append(stats.avg_len_dict(stats.avg_billing_queue,
                                               rest_model.restaurant.work_time_to
                                               - rest_model.restaurant.work_time_from))
    avg_billing_queue.append(stats.avg_len_dict(stats.avg_dishes_queue,
                                                rest_model.restaurant.work_time_to
                                                - rest_model.restaurant.work_time_from))
    avg_long_waiting_leave_count.append(stats.long_waiting_leave_counter)
    avg_serviced_count.append(stats.serviced_counter)
    avg_seated_count.append(stats.seated_counter)
    avg_no_seat_count.append(stats.no_seat_counter)
    avg_reorder_count.append(stats.reorder_counter)
    avg_disliked_menu_count.append(stats.disliked_menu_counter)
    avg_total_count.append(stats.total_counter)
    avg_total_dish_count.append(stats.count_sum(stats.dish_counter))
    avg_billed_dish_count.append(stats.count_sum(stats.billed_dish_counter))

    stats.stay_times_normal_leave = []
    stats.stay_times_bad_menu_leave = []
    stats.stay_times_long_waiting_leave = []
    stats.cook_time = []
    stats.service_time = []
    stats.delivery_time = []
    stats.dish_counter = []
    stats.billed_dish_counter = []
    stats.avg_waiting_queue = defaultdict(int)
    stats.avg_dishes_queue = defaultdict(int)
    stats.avg_billing_queue = defaultdict(int)
    stats.long_waiting_leave_counter = 0
    stats.serviced_counter = 0
    stats.seated_counter = 0
    stats.no_seat_counter = 0
    stats.reorder_counter = 0
    stats.disliked_menu_counter = 0
    stats.total_counter = 0

pretty_table = PrettyTable(["Measure", "Value"])

mean, error = confidence_interval(avg_times_normal_leave)
pretty_table.add_row(["Average stay time (no leave)",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_request_waiting)
pretty_table.add_row(["Average waiting time",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_times_bad_menu_leave)
pretty_table.add_row(["Average stay time (dislike menu)",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_times_long_waiting_leave)
pretty_table.add_row(["Average stay time (waited too long)",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_cook_time)
pretty_table.add_row(["Average cooking time",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_service_time)
pretty_table.add_row(["Average servicing time",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_delivery_time)
pretty_table.add_row(["Average delivering time",
                      utils.human_readable_time(mean) + " ± " + utils.human_readable_time(error)])

mean, error = confidence_interval(avg_dish_count, False)
pretty_table.add_row(["Average dish count",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_waiting_queue, False)
pretty_table.add_row(["Average waiting queue length",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_billing_queue, False)
pretty_table.add_row(["Average waiting for a bill queue length",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_dishes_queue, False)
pretty_table.add_row(["Average ready dishes queue length",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_long_waiting_leave_count, False)
pretty_table.add_row(["Average leave count (too long waiting)",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_serviced_count, False)
pretty_table.add_row(["Average serviced count",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_seated_count, False)
pretty_table.add_row(["Average seated count",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_no_seat_count, False)
pretty_table.add_row(["Average leave count (no free tables)",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_reorder_count, False)
pretty_table.add_row(["Average reorder count",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_disliked_menu_count, False)
pretty_table.add_row(["Average leave count (dislike menu)",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_total_count, False)
pretty_table.add_row(["Average total request count",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_total_dish_count, False)
pretty_table.add_row(["Ordered dishes", str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval(avg_billed_dish_count, False)
pretty_table.add_row(["Billed dishes", str(round(mean, 3)) + " ± " + str(round(error, 3))])

diffs = [a - b for (a, b) in zip(avg_total_dish_count, avg_billed_dish_count)]
mean, error = confidence_interval(diffs, False)
pretty_table.add_row(["Not billed dishes (because of closing)",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

mean, error = confidence_interval([a / b for (a, b) in zip(diffs, avg_total_dish_count)], False)
pretty_table.add_row(["Part of not billed dishes",
                      str(round(mean, 3)) + " ± " + str(round(error, 3))])

print(pretty_table)
