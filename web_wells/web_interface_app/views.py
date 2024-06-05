import json
import os
from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import render

from django.utils.safestring import mark_safe
# Create your views here.
import os
import random
import datetime


def debits_monitoring(request):
    html_files_folder = 'C:\\Users\\ravil\\Desktop\\well-visualisation\\pipe_system_visualize\\data_html'  # Укажите путь к папке с HTML файлами
    for dir_name in os.listdir(html_files_folder):
        if os.path.isdir(os.path.join(html_files_folder, dir_name)):
            html_files = os.listdir(os.path.join(html_files_folder, dir_name))
    folder_names = os.listdir(html_files_folder)
    files = {}

    for folder_name in folder_names:
        files[folder_name] = {}
        for file_name in html_files:
            with open(os.path.join(html_files_folder, folder_name, file_name), 'r') as file:
                files[folder_name][file_name] = file.read()

    selected_file = None
    sample_file = list(files[list(files.keys())[0]].keys())[0]
    if request.method == 'POST':
        selected_file = request.POST.get('selected_file')

    value_type = 'debits'
    if not selected_file:
        selected_file = sample_file

    context = {
        'value_types': folder_names,
        'value_type': value_type,
        'files': files[value_type],
        'selected_file': files[value_type][selected_file]
    }

    return render(request, 'web_interface_app/debits_monitoring.html', context)



def pressures_monitoring(request):
    html_files_folder = 'C:\\Users\\ravil\\Desktop\\well-visualisation\\pipe_system_visualize\\data_html'  # Укажите путь к папке с HTML файлами
    for dir_name in os.listdir(html_files_folder):
        if os.path.isdir(os.path.join(html_files_folder, dir_name)):
            html_files = os.listdir(os.path.join(html_files_folder, dir_name))
    folder_names = os.listdir(html_files_folder)
    files = {}

    for folder_name in folder_names:
        files[folder_name] = {}
        for file_name in html_files:
            with open(os.path.join(html_files_folder, folder_name, file_name), 'r') as file:
                files[folder_name][file_name] = file.read()

    selected_file = None
    sample_file = list(files[list(files.keys())[0]].keys())[0]
    if request.method == 'POST':
        selected_file = request.POST.get('selected_file')

    value_type = 'pressures'
    if not selected_file:
        selected_file = sample_file

    context = {
        'value_types': folder_names,
        'value_type': value_type,
        'files': files[value_type],
        'selected_file': files[value_type][selected_file]
    }

    return render(request, 'web_interface_app/pressures_monitoring.html', context)

def home(request):
    return render(request, 'web_interface_app/home.html')


def notifications(request):
    notification_files_path = 'C:\\Users\\ravil\\Desktop\\well-visualisation\\pipe_system_visualize\\input_data\\warnings.json'
    with open(notification_files_path, 'r', encoding='utf-8') as file:
        dc = json.load(file)

    new_dict = {}
    for item in dc:
        if 'pressure' in dc[item]:
            val = str(dc[item]['pressure'])
            new_dict[item] = {'error': ('Значение давления равно ' + val + ' Атм, что является превышением'),
                              'date': dc[item]['date']}
        elif 'debit' in dc[item]:
            val = str(dc[item]['debit'])
            new_dict[item] = {'error': ('Значение дебита слишком низкое, равно ' + val + ' м3'),
                              'date': dc[item]['date']}
    print(new_dict)
    sorted_data = dict(sorted(new_dict.items(), key=lambda item: item[1]['date']))

    context = {
        'files': sorted_data,
    }
    return render(request, 'web_interface_app/notifications.html', context)
