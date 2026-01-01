from django.urls import include, path

from .core import admin

urlpatterns = [
    path("", include("macau.redirects.urls")),
    path("-/admin/", admin.admin_site.urls),
    path("-/health/", include("health_check.urls")),
]
