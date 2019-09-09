import random
from . import constants

def generate_energy_usage_data(num_consumers, num_data):
    consumer_id_base = 1000
    consumer_ids = range(consumer_id_base, consumer_id_base + num_data)
    
    result = []
    for i in range(0, num_data):
        row_data = {}
        if i < num_consumers:
            row_data[constants.CONSUMER_ID_KEY] = consumer_id_base + i
        else:
            row_data[constants.CONSUMER_ID_KEY] = consumer_id_base + random.randint(0, num_consumers - 1)
        row_data[constants.ENERGY_KEY] = 500
        result.append(row_data)

    return result
    