from django.urls import path
from . import views


urlpatterns = [
    path("", views.ping, name="ping"),
    path("monitors/", views.monitor_list, name="monitor_list"),
    path("monitors/add/", views.add_monitor, name="add_monitor"),
]