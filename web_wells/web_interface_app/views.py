import os

from django.shortcuts import render

from django.utils.safestring import mark_safe
# Create your views here.
import os

def monitoring(request):
    html_files_folder = 'C:\\Users\\ravil\\Desktop\\well-visualisation\\pipe_system_visualize\\data_html'  # Укажите путь к папке с HTML файлами
    html_files = [file for file in os.listdir(html_files_folder) if file.endswith('.html')]

    files = {}
    for file_name in html_files:
        with open(os.path.join(html_files_folder, file_name), 'r') as file:
            files[file_name] = file.read()
    selected_file = list(files.keys())[0]
    if request.method == 'POST':
        selected_file = request.POST.get('selected_file', None)

    context = {
        'files': files,
        'selected_file': files[selected_file]
    }
    return render(request, 'web_interface_app/monitoring.html', context)


def home(request):
    return render(request, 'web_interface_app/home.html')

def about(request):
    return render(request, 'web_interface_app/about.html')

def services(request):
    return render(request, 'web_interface_app/services.html')







