import requests
import time
from datetime import timedelta
from django.utils import timezone
from .models import HealthCheck


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
    """
    Calculate uptime percentage based on health checks
    recorded within the given time period.
    """

    since = timezone.now() - timedelta(hours=hours)

    checks = HealthCheck.objects.filter(
        monitor=monitor,
        checked_at__gte=since
    )

    total_checks = checks.count()

    if total_checks == 0:
        return None

    successful_checks = checks.filter(
        success=True
    ).count()

    uptime = (
        successful_checks / total_checks
    ) * 100

    return round(uptime, 2)