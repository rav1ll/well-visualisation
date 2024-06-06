import json
import os
import random
from collections import defaultdict
from datetime import datetime, timedelta

# with open(os.path.join('input_data', 'output1.json'), 'r', encoding='utf-8') as fc:
#     dc = json.load(fc)
#
#
# pipes = []
# pipe_data = dc['data']
#
# for item in pipe_data:
#     if item['id'] not in pipes:
#         pipes.append(item['id'])
# data_dct = {}
#
# for item in pipes:
#     random_pressure = random.randint(10,75)
#     random_debit = random.randint(3,26)
#     data_dct[item] = {'pressure': random_pressure, 'debit': random_debit}
#
#
# with open("input_data/pipe_values.json", "w", encoding='utf-8') as json_file:
#     json.dump(data_dct, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))


with open("input_data/pipe_values.json", "r", encoding='utf-8') as fc:
    dc = json.load(fc)


    start_date = datetime(2022, 1, 1)  # Начальная дата
    end_date = datetime(2022, 12, 31)  # Конечная дата
    random_date = start_date + (end_date - start_date) * random.random()



    for item in dc:
        random_time = timedelta(seconds=random.randint(0, 24 * 60 * 60 - 1))  # От 00:00:00 до 23:59:59
        random_datetime = random_date + random_time
        original_datetime = datetime.strptime(str(random_datetime), '%Y-%m-%d %H:%M:%S.%f')
        formatted_datetime = original_datetime.strftime('%Y-%m-%d %H:%M:%S')
        dc[item]['time'] = formatted_datetime

    with open("input_data/pipe_values_ext.json", "w", encoding='utf-8') as json_file:
        json.dump(dc, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))
