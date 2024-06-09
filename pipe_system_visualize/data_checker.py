import json
import os
import random
import datetime

with open(os.path.join('input_data', 'pipe_values_ext.json'), 'r', encoding='utf-8') as fc:
    dc = json.load(fc)

with open(os.path.join('input_data', 'final_pipe_data.json'), 'r', encoding='utf-8') as fc:
    dc1 = json.load(fc)
pipe_data = dc1['data']
with open(os.path.join('input_data', 'config.json'), 'r') as fc:
    conf = json.load(fc)

optimal_pressure = conf['pressure_optimal_value']
pressure_deviation = conf['pressure_deviation']

min_optimal_debit = conf['min_debit']

warning_dict = {}

for item in dc:

    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 12, 31)

    random_days = (end_date - start_date).days
    random_date = datetime.datetime.strftime(start_date + datetime.timedelta(days=random.randint(0, random_days)), '%#d %b %Y')



    curr_pressure = dc[item]['pressure']
    curr_debit = dc[item]['debit']
    for pipe_dct in pipe_data:
        if int(item) == int(pipe_dct['id']):
            curr_nam = pipe_dct['cnam']
            curr_id = str(pipe_dct['id'])
            curr_date = dc[curr_id]['time']

    # хардкод обработка некорректных данных
    if ' - Скв' not in curr_nam:



        if curr_pressure <= optimal_pressure * (1 - 2*pressure_deviation) or curr_pressure >= optimal_pressure * (1 + 2*pressure_deviation):
            if curr_nam not in warning_dict:
                warning_dict[curr_nam] = {}
            warning_dict[curr_nam]['pressure'] = curr_pressure
            warning_dict[curr_nam]['date'] = curr_date
            warning_dict[curr_nam]['id'] = curr_id

        if curr_debit <= min_optimal_debit:
            if curr_nam not in warning_dict:
                warning_dict[curr_nam] = {}
                warning_dict[curr_nam]['date'] = curr_date
                warning_dict[curr_nam]['id'] = curr_id
            warning_dict[curr_nam]['debit'] = curr_debit

with open("input_data/warnings.json", "w", encoding='utf-8') as json_file:
    json.dump(warning_dict, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))
