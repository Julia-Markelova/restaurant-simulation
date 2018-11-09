from prettytable import PrettyTable

if __name__ == '__main__':
    from restaurant_simulation import stats, model, utils

    name = "restaurant_model"

    restaurant_model = model.Model(open('parameters.json'))
    restaurant_model.run()

    pretty_table = PrettyTable(["Measure", "Value"])

    pretty_table.add_row(["Average stay time (no leave)",
                          stats.avg_stay_time(stats.stay_times_normal_leave)])
    pretty_table.add_row(["Average stay time (dislike menu)",
                          stats.avg_stay_time(stats.stay_times_bad_menu_leave)])
    pretty_table.add_row(["Average stay time (waited too long)",
                          stats.avg_stay_time(stats.stay_times_long_waiting_leave)])
    pretty_table.add_row(["Average cooking time",
                          stats.avg_stay_time(stats.cook_time)])
    pretty_table.add_row(["Average servicing time",
                          stats.avg_stay_time(stats.service_time)])
    pretty_table.add_row(["Average delivering time",
                          stats.avg_stay_time(stats.delivery_time)])
    pretty_table.add_row(["Average dish count",
                          stats.count_avg(stats.dish_counter, 3)])

    print(pretty_table)

    pretty_table = PrettyTable(["Waiter id", "Load"])

    for key, value in stats.worker_load(stats.waiter_hours,
                                        restaurant_model.global_time - restaurant_model.restaurant.work_time_from) \
            .items():
        pretty_table.add_row([key, value])

    print(pretty_table)

    pretty_table = PrettyTable(["Cooker id", "Load"])

    for key, value in stats.worker_load(stats.cooker_hours,
                                        restaurant_model.global_time - restaurant_model.restaurant.work_time_from) \
            .items():
        pretty_table.add_row([key, value])

    print(pretty_table)

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

    print(restaurant_model.restaurant.tables)
    # for event in restaurant_model.next_events:
