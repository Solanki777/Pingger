from django.db import models


class Monitor(models.Model):

    name = models.CharField(max_length=100)

    url = models.URLField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    check_interval = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

class HealthCheck(models.Model):

    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
        related_name="health_checks"
    )

    status_code = models.IntegerField(
        null=True,
        blank=True
    )

    response_time = models.FloatField(
        null=True,
        blank=True
    )

    success = models.BooleanField(
        default=False
    )

    error = models.TextField(
        null=True,
        blank=True
    )

    checked_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.monitor.name} - {self.checked_at}"