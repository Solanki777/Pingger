import requests
import time

from .models import HealthCheck


def perform_health_check(monitor):

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
            status_code=status_code,
            response_time=response_time,
            success=success
        )

        return health_check

    except requests.Timeout:

        return HealthCheck.objects.create(
            monitor=monitor,
            success=False,
            error="Request timed out"
        )

    except requests.ConnectionError:

        return HealthCheck.objects.create(
            monitor=monitor,
            success=False,
            error="Connection failed"
        )

    except requests.RequestException as e:

        return HealthCheck.objects.create(
            monitor=monitor,
            success=False,
            error=str(e)
        )