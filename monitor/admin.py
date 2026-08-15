from django.contrib import admin
from .models import Monitor,HealthCheck


admin.site.register(Monitor)
admin.site.register(HealthCheck)