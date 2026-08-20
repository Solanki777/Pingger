from django.shortcuts import render,redirect
import json
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from .models import Monitor
from .services import perform_health_check
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

def monitor_logs_api(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    health_checks = monitor.health_checks.order_by(
        "-checked_at"
    )[:20]

    logs = []

    for check in health_checks:

        logs.append({
            "time": check.checked_at.strftime("%H:%M:%S"),
            "status_code": check.status_code,
            "response_time": check.response_time,
            "success": check.success,
            "check_type": check.check_type,
            "error": check.error,
        })

    return JsonResponse({
        "logs": logs
    })

def check_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    health_check = perform_health_check(
    monitor,
    check_type="user"
)

    return render(
        request,
        "check_result.html",
        {
            "monitor": monitor,
            "health_check": health_check,
        }
    )


def edit_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    if request.method == "POST":

        monitor.name = request.POST.get("name")
        monitor.url = request.POST.get("url")

        new_interval = int(
            request.POST.get("check_interval")
        )

        monitor.check_interval = new_interval

        monitor.save()

        periodic_task = PeriodicTask.objects.filter(
        name=f"monitor-{monitor.id}"
        ).first()

        if periodic_task:

            schedule, created = IntervalSchedule.objects.get_or_create(
                every=new_interval,
                period=IntervalSchedule.MINUTES,
            )

            periodic_task.interval = schedule
            periodic_task.save()

        return redirect("monitor_list")

    return render(
        request,
        "edit_monitor.html",
        {
            "monitor": monitor
        }
    )

def delete_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    if request.method == "POST":

        PeriodicTask.objects.filter(
            name=f"monitor-{monitor.id}"
        ).delete()

        monitor.delete()

        return redirect("monitor_list")

    return redirect("monitor_list")


def add_monitor(request):

    if request.method == "POST":

        name = request.POST.get("name")
        url = request.POST.get("url")
        check_interval = int(
            request.POST.get("check_interval")
        )

        monitor = Monitor.objects.create(
            name=name,
            url=url,
            check_interval=check_interval
        )

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=check_interval,
            period=IntervalSchedule.MINUTES,
        )

        PeriodicTask.objects.create(
        interval=schedule,
        name=f"monitor-{monitor.id}",
        task="monitor.tasks.check_monitor_task",
        args=json.dumps([monitor.id]),
    )

        return redirect("monitor_list")

    return render(
        request,
        "add_monitor.html"
    )



def monitor_list(request):
    monitors = Monitor.objects.all()
    return render(
        request,
        "monitor_list.html",
        {
            "monitors": monitors
        }
    )




def monitor_details(request, id):

    monitor = Monitor.objects.get(id=id)

    health_checks = monitor.health_checks.order_by(
        "-checked_at"
    )

    latest_check = health_checks.first()

    return render(
        request,
        "monitor_details.html",
        {
            "monitor": monitor,
            "health_checks": health_checks,
            "latest_check": latest_check,
        }
    )