from celery import shared_task

from .models import Monitor
from .services import perform_health_check


@shared_task
def check_monitor_task(monitor_id):

    monitor = Monitor.objects.get(id=monitor_id)

    health_check = perform_health_check(monitor)

    return {
        "monitor_id": monitor_id,
        "success": health_check.success,
        "status_code": health_check.status_code,
        "response_time": health_check.response_time,
    }

@shared_task
def check_all_monitors():

    monitors = Monitor.objects.filter(
        is_active=True
    )

    for monitor in monitors:
        check_monitor_task.delay(monitor.id)