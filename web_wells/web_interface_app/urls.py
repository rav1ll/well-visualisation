from django.urls import path
from . import views

urlpatterns = [
    path('monitoring', views.monitoring, name='monitoring'),
    path('', views.home, name='home'),
    path('services', views.services, name='services'),

]