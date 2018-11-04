from model import Model

restaurant_model = Model(open('parameters.json'))

[print(interval.interval) for interval in restaurant_model.intervals]
