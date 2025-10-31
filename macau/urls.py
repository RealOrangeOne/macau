from django.urls import path, include
from . import admin

urlpatterns = [
    path("admin/", admin.admin_site.urls),
    path("-/health/", include("health_check.urls")),
    path("", include("macau.redirects.urls")),
]
