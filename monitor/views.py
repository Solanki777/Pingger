from django.shortcuts import render,redirect
import requests
import time
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Monitor,HealthCheck

def add_monitor(request):
    if request.method == "POST":
        name = request.POST.get("name")
        url = request.POST.get("url")

        Monitor.objects.create(
            name = name,
            url = url
        )
        return redirect("monitor_list")
    return render(request,"add_monitor.html")

def monitor_list(request):
    monitors = Monitor.objects.all()
    return render(
        request,
        "monitor_list.html",
        {
            "monitors": monitors
        }
    )


@ensure_csrf_cookie
def ping(request):

    result = None
    response_time = None
    status_code = None
    status_type = None

    if request.method == "POST":

        url = request.POST.get("url")

        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()

            response_time = round(
                (end_time-start_time) *1000,2
            )
            status_code = response.status_code


            if 200 <= status_code < 300:
                result = "Website is healthy"
                status_type = "success"

            elif 300 <= status_code < 400:
                result = "Website is reachable but redirecting"
                status_type = "warning"

            elif 400 <= status_code < 500:
                result = "Website is reachable but returned a client error"
                status_type = "warning"

            elif 500 <= status_code < 600:
                result = "Website is reachable but returned a server error"
                status_type = "danger"


        except requests.Timeout:

            result = "Website request timed out"
            status_type = "danger"

        except requests.ConnectionError:

            result = "Could not connect to website"
            status_type = "danger"

        except requests.RequestException:

            result = "Website check failed"
            status_type = "danger"

    return render(request,"ping.html",
                {
                    "result":result,
                    "status_code":status_code,
                    "response_time":response_time,
                     "status_type":status_type })


def check_monitor(request, id):

    monitor = Monitor.objects.get(id=id)

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

        HealthCheck.objects.create(
            monitor=monitor,
            status_code=status_code,
            response_time=response_time,
            success=success
        )

        result = "Website is healthy" if success else "Website returned an error"

    except requests.Timeout:

        HealthCheck.objects.create(
            monitor=monitor,
            success=False,
            error="Request timed out"
        )

        result = "Request timed out"

    except requests.ConnectionError:

        HealthCheck.objects.create(
            monitor=monitor,
            success=False,
            error="Connection failed"
        )

        result = "Connection failed"

    except requests.RequestException as e:

        HealthCheck.objects.create(
            monitor=monitor,
            success=False,
            error=str(e)
        )

        result = "Health check failed"

    return render(
        request,
        "check_result.html",
        {
            "monitor": monitor,
            "result": result,
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