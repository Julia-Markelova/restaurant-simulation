from model import Model

restaurant_model = Model(open('parameters.json'))
restaurant_model.run()
print("Сели за стол:", restaurant_model.count,
      "Не хватило стола:", restaurant_model.lost_counter,
      "Обслужены:", restaurant_model.serviced,
      "Всего сгенерировано:", restaurant_model.all)

# for event in restaurant_model.next_events:
