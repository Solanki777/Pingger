from django.urls import path
from . import views


urlpatterns = [
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

path(
    "<int:id>/edit/",
    views.edit_monitor,
    name="edit_monitor"
),

path(
    "monitors/<int:id>/toggle/",
    views.toggle_monitor,
    name="toggle_monitor"
),


path(
    "<int:id>/delete/",
    views.delete_monitor,
    name="delete_monitor"
),
path(
    "monitors/<int:id>/logs/",
    views.monitor_logs_api,
    name="monitor_logs_api"
),



]