from django.urls import include, path
from health_check.views import HealthCheckView

from .core import admin

urlpatterns = [
    path("", include("macau.redirects.urls")),
    path("-/admin/", admin.admin_site.urls),
    path("-/health/", HealthCheckView.as_view(checks=["health_check.Database"])),
]
