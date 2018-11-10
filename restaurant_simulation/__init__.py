"""
Just for pretty print
"""
from prettytable import PrettyTable

if __name__ == '__main__':
    from restaurant_simulation import stats, model, utils

    name = "restaurant_model"

    restaurant_model = model.Model(open('parameters.json'))
    restaurant_model.run()

    pretty_table = PrettyTable(["Measure", "Value"])

    pretty_table.add_row(["Average stay time (no leave)",
                          stats.avg_time(stats.stay_times_normal_leave)])
    pretty_table.add_row(["Average waiting time",
                          stats.avg_waiting_time(stats.request_waiting)])
    pretty_table.add_row(["Average stay time (dislike menu)",
                          stats.avg_time(stats.stay_times_bad_menu_leave)])
    pretty_table.add_row(["Average stay time (waited too long)",
                          stats.avg_time(stats.stay_times_long_waiting_leave)])
    pretty_table.add_row(["Average cooking time",
                          stats.avg_time(stats.cook_time)])
    pretty_table.add_row(["Average servicing time",
                          stats.avg_time(stats.service_time)])
    pretty_table.add_row(["Average delivering time",
                          stats.avg_time(stats.delivery_time)])
    pretty_table.add_row(["Average dish count",
                          stats.count_avg(stats.dish_counter, 3)])
    pretty_table.add_row(["Average waiting queue length",
                          stats.avg_len_dict(stats.avg_waiting_queue,
                                             restaurant_model.restaurant.work_time_to
                                             - restaurant_model.restaurant.work_time_from)])
    pretty_table.add_row(["Average waiting for a bill queue length",
                          stats.avg_len_dict(stats.avg_billing_queue,
                                             restaurant_model.restaurant.work_time_to
                                             - restaurant_model.restaurant.work_time_from)])
    pretty_table.add_row(["Average ready dishes queue length",
                          stats.avg_len_dict(stats.avg_dishes_queue,
                                             restaurant_model.restaurant.work_time_to
                                             - restaurant_model.restaurant.work_time_from)])

    print(pretty_table)

    header = ["Cooker id"]
    header.extend(
        [utils.human_readable_time(period.fromInterval)
         + "-"
         + utils.human_readable_time(period.toInterval)
         if not period.last
         else utils.human_readable_time(period.fromInterval)
         + "-" + utils.human_readable_date_time(restaurant_model.global_time)
         for period
         in restaurant_model.intervals])
    header.append("Total")

    pretty_table = PrettyTable(header)

    for key, value in stats.multi_period_worker_load(stats.cooker_hours, restaurant_model.global_time).items():
        row = [key]
        row.extend(value)
        row.append(stats.total_worker_load(key, stats.cooker_hours, restaurant_model.global_time))
        pretty_table.add_row(row)

    print(pretty_table.get_string(title="Load by period"))

    pretty_table = PrettyTable(["Measure", "Value"])
    pretty_table.add_row(["Missed the table", stats.no_seat_counter])
    pretty_table.add_row(["Took a table", stats.seated_counter])
    pretty_table.add_row(["Leave (disliking menu)", stats.disliked_menu_counter])
    pretty_table.add_row(["Leave (waited too long)", stats.long_waiting_leave_counter])
    pretty_table.add_row(["Serviced", stats.serviced_counter])
    pretty_table.add_row(["Took an extra order", stats.reorder_counter])
    pretty_table.add_row(["Total", stats.total_counter])

    print(pretty_table)

    pretty_table = PrettyTable(["Measure", "Value"])
    pretty_table.add_row(["Ordered dishes", stats.count_sum(stats.dish_counter)])
    pretty_table.add_row(["Billed dishes", stats.count_sum(stats.billed_dish_counter)])
    pretty_table.add_row(["Not billed dishes (because of closing)",
                          stats.count_sum(stats.dish_counter) - stats.count_sum(stats.billed_dish_counter)])
    pretty_table.add_row(["Part of not billed dishes",
                          round((stats.count_sum(stats.dish_counter) - stats.count_sum(stats.billed_dish_counter)) /
                                stats.count_sum(stats.dish_counter), 3)])

    print(pretty_table)

    header = ["Waiter id"]
    header.extend(
        [utils.human_readable_time(period.fromInterval)
         + "-"
         + utils.human_readable_time(period.toInterval) if not period.last
         else utils.human_readable_time(period.fromInterval)
         + "-" + utils.human_readable_date_time(restaurant_model.global_time) for period
         in restaurant_model.intervals])
    header.append("Total")

    pretty_table = PrettyTable(header)

    for key, value in stats.multi_period_worker_load(stats.waiter_hours, restaurant_model.global_time).items():
        row = [key]
        row.extend(value)
        row.append(stats.total_worker_load(key, stats.waiter_hours, restaurant_model.global_time))
        pretty_table.add_row(row)

    print(pretty_table.get_string(title="Load by period"))

    # for event in restaurant_model.next_events:
