from model import Model

restaurant_model = Model(open('parameters.json'))
for interval in restaurant_model.intervals:
    print(interval.__dict__)
restaurant_model.run()
print(restaurant_model.count, restaurant_model.lost_counter)

# for event in restaurant_model.next_events:
