from django.urls import path
from . import views


urlpatterns = [
    path("", views.ping, name="ping"),
    path("monitors/", views.monitor_list, name="monitor_list"),
    path("monitors/add/", views.add_monitor, name="add_monitor"),
    path(
    "monitors/<int:id>/check/",
    views.check_monitor,
    name="check_monitor"
),
path(
    "monitors/<int:id>/",
    views.monitor_details,
    name="monitor_details"
),
]