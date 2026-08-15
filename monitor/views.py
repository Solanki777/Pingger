from django.shortcuts import render,redirect

from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Monitor
from .services import perform_health_check


def check_monitor(request, id):

    monitor = Monitor.objects.get(id=id)

    health_check = perform_health_check(monitor)

    if health_check.success:
        result = "Website is healtsdkfkadsjhy"
    else:
        result = "Website check fadjf;alsdfailed"

    return render(
        request,
        "check_result.html",
        {
            "monitor": monitor,
            "result": result,
            "health_check": health_check,
        }
    )





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