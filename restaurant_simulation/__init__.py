from prettytable import PrettyTable

if __name__ == '__main__':
    from restaurant_simulation import stats, model, utils

    name = "restaurant_model"

    restaurant_model = model.Model(open('parameters.json'))
    restaurant_model.run()
    print("---------------------------------------------\n")
    print("Сели за стол:", stats.seated_counter, "\n"
                                                 "Не хватило стола:", stats.no_seat_counter, "\n"
                                                                                             "Обслужены:",
          stats.serviced_counter, "\n"
                                  "Слишком долго ждали:", stats.long_waiting_leave_counter, "\n"
                                                                                            "Всего поступило:",
          stats.total_counter, "\n"
                               "Дозаказали:", stats.reorder_counter, "\n"
                                                                     "Ушли без заказа:", stats.disliked_menu_counter)

    print("---------------------------------------------\n")
    print("norm:", list(map(lambda t: utils.human_readable_time(t), stats.stay_times_normal_leave)), "\n"
                                                                                                     "bad menu:",
          list(map(lambda t: utils.human_readable_time(t), stats.stay_times_bad_menu_leave)), "\n"
                                                                                              "long waiting:",
          list(map(lambda t: utils.human_readable_time(t), stats.stay_times_long_waiting_leave)))

    print("---------------------------------------------\n")
    print("avg_norm:", utils.human_readable_time(round(stats.avg_stay_time(stats.stay_times_normal_leave))), "\n"
                                                                                                             "avg_bad_menu:",
          utils.human_readable_time(round(stats.avg_stay_time(stats.stay_times_bad_menu_leave))), "\n"
                                                                                                  "avg_long_waiting:",
          utils.human_readable_time(round(stats.avg_stay_time(stats.stay_times_long_waiting_leave))), "\n"
                                                                                                      "avg_cook_time:",
          utils.human_readable_time(round(stats.avg_stay_time(stats.cook_time))), "\n"
                                                                                  "avg_service_time:",
          utils.human_readable_time(round(stats.avg_stay_time(stats.service_time))), "\n"
                                                                                     "avg_delivery_time:",
          utils.human_readable_time(round(stats.avg_stay_time(stats.delivery_time))), "\n"
                                                                                      "avg_waiter_time:",
          utils.human_readable_time(
              round(stats.avg_stay_time(stats.service_time) + stats.avg_stay_time(stats.delivery_time))), "\n"
                                                                                                          "avg_dish_count:",
          (stats.avg_stay_time(stats.dish_counter)), "\n")

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
    # for event in restaurant_model.next_events:
