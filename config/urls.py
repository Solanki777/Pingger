from django.urls import path,include
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns =[
    path("admin/",admin.site.urls),
    path("",include("monitor.urls")),
    path("accounts/", include("allauth.urls")),

    path(
        "favicon.ico",
        RedirectView.as_view(
            url="/static/monitor/images/pingger-icon.png",
            permanent=False
        )),
]
