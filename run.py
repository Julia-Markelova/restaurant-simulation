from restaurant_simulation import model

rest_model = model.Model(open('parameters.json'))

rest_model.run()
