from django.shortcuts import get_object_or_404, redirect, render
import json

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Monitor, MonitorState, Alert
from .services import (
    perform_health_check,
    calculate_uptime,
)


@login_required
def monitor_logs_api(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
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


@login_required
def toggle_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
    )

    periodic_task = PeriodicTask.objects.filter(
        name=f"monitor-{monitor.id}"
    ).first()

    monitor.is_active = not monitor.is_active
    monitor.save()

    if periodic_task:

        periodic_task.enabled = monitor.is_active
        periodic_task.save()

    MonitorState.objects.create(
        monitor=monitor,
        is_active=monitor.is_active
    )

    return JsonResponse({
        "success": True,
        "is_active": monitor.is_active,
    })


@login_required
def check_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
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


@login_required
def edit_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
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

            schedule, created = (
                IntervalSchedule.objects.get_or_create(
                    every=new_interval,
                    period=IntervalSchedule.MINUTES,
                )
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


@login_required
def delete_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        PeriodicTask.objects.filter(
            name=f"monitor-{monitor.id}"
        ).delete()

        monitor.delete()

        return redirect("monitor_list")

    return redirect("monitor_list")


@login_required
def add_monitor(request):

    if request.method == "POST":

        name = request.POST.get("name")

        url = request.POST.get("url")

        check_interval = int(
            request.POST.get("check_interval")
        )

        monitor = Monitor.objects.create(
            user=request.user,
            name=name,
            url=url,
            check_interval=check_interval
        )

        MonitorState.objects.create(
            monitor=monitor,
            is_active=True
        )

        schedule, created = (
            IntervalSchedule.objects.get_or_create(
                every=check_interval,
                period=IntervalSchedule.MINUTES,
            )
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


@login_required
def monitor_list(request):

    monitors = Monitor.objects.filter(
        user=request.user
    )

    for monitor in monitors:

        monitor.latest_check = (
            monitor.health_checks
            .order_by("-checked_at")
            .first()
        )

        monitor.uptime_24h = calculate_uptime(
            monitor,
            hours=24
        )

        monitor.uptime_7d = calculate_uptime(
            monitor,
            hours=24 * 7
        )

        monitor.uptime_30d = calculate_uptime(
            monitor,
            hours=24 * 30
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


@login_required
def monitor_details(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
    )

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


@login_required
def monitor_graph_api(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id,
        user=request.user
    )

    health_checks = monitor.health_checks.order_by(
        "checked_at"
    )[:100]

    data = []

    for check in health_checks:

        data.append({
            "time": timezone.localtime(
                check.checked_at
            ).strftime("%H:%M"),

            "response_time": check.response_time,

            "success": check.success,
        })

    return JsonResponse({
        "data": data
    })


@login_required
def alerts_api(request):

    alerts = Alert.objects.filter(
        user=request.user
    ).select_related(
        "monitor"
    ).order_by(
        "-created_at"
    )[:20]

    data = []

    for alert in alerts:

        data.append({
            "id": alert.id,

            "monitor": alert.monitor.name,

            "type": alert.alert_type,

            "message": alert.message,

            "is_read": alert.is_read,

            "created_at": timezone.localtime(
                alert.created_at
            ).strftime("%Y-%m-%d %H:%M:%S"),
        })

    unread_count = Alert.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        "alerts": data,
        "unread_count": unread_count,
    })


@login_required
def mark_alert_read(request, id):

    alert = get_object_or_404(
        Alert,
        id=id,
        user=request.user
    )

    alert.delete()

    return JsonResponse({
        "success": True
    })