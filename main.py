from model import Model

restaurant_model = Model(open('parameters.json'))
restaurant_model.run()
print("---------------------------------------------\n")
print("Сели за стол:", restaurant_model.seated_count, "\n"
      "Не хватило стола:", restaurant_model.lost_counter, "\n"
      "Обслужены:", restaurant_model.serviced, "\n"
      "Слишком долго ждали:", restaurant_model.bad_leave_counter, "\n"
      "Всего поступило:", restaurant_model.all, "\n"
      "Дозаказали:", restaurant_model.reordered, "\n"
      "Ушли без заказа:", restaurant_model.dislike_menu)

# for event in restaurant_model.next_events:
