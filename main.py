from model import Model


restaurant_model = Model(open('parameters.json'))

[print(table.size) for table in restaurant_model.tables]
