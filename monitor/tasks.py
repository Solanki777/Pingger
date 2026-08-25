from celery import shared_task
from django.core.mail import send_mail

from .models import Monitor, Alert
from .services import perform_health_check


@shared_task
def check_monitor_task(monitor_id):

    monitor = Monitor.objects.get(
        id=monitor_id
    )

    previous_check = (
        monitor.health_checks
        .exclude(check_type="user")
        .order_by("-checked_at")
        .first()
    )

    health_check = perform_health_check(
        monitor,
        check_type="celery"
    )

    # --------------------------------------------------
    # ALERT: WEBSITE DOWN
    # --------------------------------------------------

    if not health_check.success:

        # Send alert only when the previous state was UP
        # or when there was no previous check.

        should_alert = (
            previous_check is None
            or previous_check.success
        )

        if should_alert and monitor.user:

            message = (
                f"Your monitored website is currently DOWN.\n\n"
                f"Website: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Status: Request failed or timed out.\n\n"
                f"Pingger will continue monitoring the website "
                f"and notify you when it is back online."
            )

            Alert.objects.create(
                user=monitor.user,
                monitor=monitor,
                alert_type="down",
                message=message,
            )

            send_mail(
                subject=f"🔴 Website Down - {monitor.name}",
                message=message,
                from_email=None,
                recipient_list=[
                    monitor.user.email
                ],
                fail_silently=False,
            )

    # --------------------------------------------------
    # ALERT: WEBSITE BACK ONLINE
    # --------------------------------------------------

    else:

        # Send recovery alert only when the previous state was DOWN.

        should_alert = (
            previous_check is not None
            and not previous_check.success
        )

        if should_alert and monitor.user:

            message = (
                f"Good news! Your website is back online.\n\n"
                f"Website: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Status Code: {health_check.status_code}\n"
                f"Response Time: "
                f"{health_check.response_time} ms\n\n"
                f"Pingger will continue monitoring your website."
            )

            Alert.objects.create(
                user=monitor.user,
                monitor=monitor,
                alert_type="up",
                message=message,
            )

            send_mail(
                subject=f"🟢 Website Back Online - {monitor.name}",
                message=message,
                from_email=None,
                recipient_list=[
                    monitor.user.email
                ],
                fail_silently=False,
            )

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

        check_monitor_task.delay(
            monitor.id
        )