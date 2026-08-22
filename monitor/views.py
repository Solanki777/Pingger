from django.shortcuts import render,redirect
import json
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from .models import Monitor
from .services import (
    perform_health_check,
    calculate_uptime,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.utils import timezone



def monitor_logs_api(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    health_checks = monitor.health_checks.order_by(
        "-checked_at"
    )[:20]

    latest_check = health_checks.first()

    logs = []

    for check in health_checks:

        logs.append({
            "time": timezone.localtime(
    check.checked_at
).strftime("%H:%M:%S"),
            "status_code": check.status_code,
            "response_time": check.response_time,
            "success": check.success,
            "check_type": check.check_type,
            "error": check.error,
        })

    latest = None

    if latest_check:

        latest = {
            "status_code": latest_check.status_code,
            "response_time": latest_check.response_time,
            "success": latest_check.success,
            "error": latest_check.error,
            "checked_at": timezone.localtime(
                latest_check.checked_at
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }

    return JsonResponse({
        "logs": logs,
        "latest": latest,
    })

def toggle_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    periodic_task = PeriodicTask.objects.filter(
        name=f"monitor-{monitor.id}"
    ).first()

    monitor.is_active = not monitor.is_active
    monitor.save()

    if periodic_task:
        periodic_task.enabled = monitor.is_active
        periodic_task.save()

    return JsonResponse({
        "success": True,
        "is_active": monitor.is_active,
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

    for monitor in monitors:
        monitor.latest_check = monitor.health_checks.order_by(
            "-checked_at"
        ).first()

        monitor.uptime_24h = calculate_uptime(
        monitor,
        hours=24
    )

    total_monitors = monitors.count()

    active_monitors = monitors.filter(
        is_active=True
    ).count()

    paused_monitors = monitors.filter(
        is_active=False
    ).count()

    up_monitors = sum(
        1
        for monitor in monitors
        if monitor.latest_check
        and monitor.latest_check.success
    )

    down_monitors = sum(
        1
        for monitor in monitors
        if monitor.latest_check
        and not monitor.latest_check.success
    )

    return render(
        request,
        "monitor_list.html",
        {
            "monitors": monitors,
            "total_monitors": total_monitors,
            "active_monitors": active_monitors,
            "paused_monitors": paused_monitors,
            "up_monitors": up_monitors,
            "down_monitors": down_monitors,
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