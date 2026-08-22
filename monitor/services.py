import requests
import time
from datetime import timedelta
from django.utils import timezone
from .models import HealthCheck, MonitorState



def perform_health_check(monitor, check_type="user"):

    start_time = time.time()

    try:
        response = requests.get(
            monitor.url,
            timeout=10
        )

        end_time = time.time()

        response_time = round(
            (end_time - start_time) * 1000,
            2
        )

        status_code = response.status_code

        success = 200 <= status_code < 300

        health_check = HealthCheck.objects.create(
            monitor=monitor,
            check_type=check_type,
            status_code=status_code,
            response_time=response_time,
            success=success
        )

        return health_check

    except requests.Timeout:

        return HealthCheck.objects.create(
            monitor=monitor,
            check_type=check_type,
            success=False,
            error="Request timed out"
        )

    except requests.ConnectionError:

        return HealthCheck.objects.create(
            monitor=monitor,
            check_type=check_type,
            success=False,
            error="Connection failed"
        )

    except requests.RequestException as e:

        return HealthCheck.objects.create(
            monitor=monitor,
            check_type=check_type,
            success=False,
            error=str(e)
        )



def calculate_uptime(monitor, hours=24):

    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours)

    states = list(
        MonitorState.objects.filter(
            monitor=monitor,
            changed_at__lte=end_time
        ).order_by("changed_at")
    )

    if not states:
        return None

    checks = list(
        HealthCheck.objects.filter(
            monitor=monitor,
            checked_at__gte=start_time,
            checked_at__lte=end_time
        ).order_by("checked_at")
    )

    if not checks:
        return None

    uptime_seconds = 0
    monitored_seconds = 0

    current_active = False
    state_index = 0
    check_index = 0
    current_check = None

    current_time = start_time

    while current_time < end_time:

        # Update monitor state
        while (
            state_index < len(states)
            and states[state_index].changed_at <= current_time
        ):
            current_active = states[state_index].is_active
            state_index += 1

        # Find latest health check at or before current time
        while (
            check_index < len(checks)
            and checks[check_index].checked_at <= current_time
        ):
            current_check = checks[check_index]
            check_index += 1

        # Determine next event
        next_state_time = end_time

        if state_index < len(states):
            next_state_time = states[state_index].changed_at

        next_check_time = end_time

        if check_index < len(checks):
            next_check_time = checks[check_index].checked_at

        next_time = min(
            next_state_time,
            next_check_time,
            end_time
        )

        if next_time <= current_time:
            current_time += timedelta(seconds=1)
            continue

        duration = (
            next_time - current_time
        ).total_seconds()

        # Only count time while monitoring is ACTIVE
        if current_active:

            monitored_seconds += duration

            if current_check and current_check.success:
                uptime_seconds += duration

        current_time = next_time

    if monitored_seconds <= 0:
        return None

    uptime = (
        uptime_seconds /
        monitored_seconds
    ) * 100

    return round(
        max(0, min(100, uptime)),
        2
    )