from model import Model

restaurant_model = Model(open('parameters.json'))

[print(event.__dict__, event.what.__dict__) for event in restaurant_model.next_events]
