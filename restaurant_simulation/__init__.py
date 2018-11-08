from restaurant_simulation import stats, model

name = "restaurant_model"

restaurant_model = model.Model(open('parameters.json'))
restaurant_model.run()
print("---------------------------------------------\n")
print("Сели за стол:", stats.seated_counter, "\n"
      "Не хватило стола:", stats.no_seat_counter, "\n"
      "Обслужены:", stats.serviced_counter, "\n"
      "Слишком долго ждали:", stats.long_waiting_leave_counter, "\n"
      "Всего поступило:", stats.total_counter, "\n"
      "Дозаказали:", stats.reorder_counter, "\n"
      "Ушли без заказа:", stats.disliked_menu_counter)

# for event in restaurant_model.next_events:
