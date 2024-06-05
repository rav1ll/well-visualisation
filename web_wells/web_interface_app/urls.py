from django.urls import path
from . import views

urlpatterns = [
    path('debits_monitoring', views.debits_monitoring, name='debits_monitoring'),
    path('pressures_monitoring', views.pressures_monitoring, name='pressures_monitoring'),
    path('', views.home, name='home'),
    path('notifications', views.notifications, name='notifications'),

]