from django.shortcuts import render,redirect

from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Monitor
from .services import perform_health_check
from django.shortcuts import get_object_or_404, redirect, render


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


def edit_monitor(request, id):

    monitor = get_object_or_404(
        Monitor,
        id=id
    )

    if request.method == "POST":

        monitor.name = request.POST.get("name")
        monitor.url = request.POST.get("url")
        monitor.check_interval = request.POST.get(
            "check_interval"
        )

        monitor.save()

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

        monitor.delete()

        return redirect("monitor_list")

    return redirect("monitor_list")





def add_monitor(request):

    if request.method == "POST":

        name = request.POST.get("name")
        url = request.POST.get("url")
        check_interval = request.POST.get("check_interval")

        Monitor.objects.create(
            name=name,
            url=url,
            check_interval=check_interval
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