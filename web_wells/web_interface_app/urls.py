from django.urls import path
from . import views

urlpatterns = [
    path('monitoring', views.monitoring, name='monitoring'),
    path('', views.home, name='home'),
    path('notifications', views.notifications, name='notifications'),

]