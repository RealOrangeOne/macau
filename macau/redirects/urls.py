from django.core.validators import URLValidator
from django.urls import path, re_path

from . import views

app_name = "redirects"

urlpatterns = [
    path("<slug:slug>", views.HandleRedirectView.as_view(), name="redirect"),
    # Duplicate the URL definition to allow for optional trailing slash
    path("<slug:slug>/", views.HandleRedirectView.as_view()),
    re_path(
        f"({URLValidator.regex.pattern})",  # type: ignore[union-attr]
        views.RedirectCreateView.as_view(),
        name="create",
    ),
    path(
        "<slug:slug>.svg",
        views.RedirectQRCodeView.as_view(),
        name="qrcode",
        kwargs={"image_format": "svg"},
    ),
    path(
        "<slug:slug>.png",
        views.RedirectQRCodeView.as_view(),
        name="qrcode-png",
        kwargs={"image_format": "png"},
    ),
    path("", views.RootRedirectView.as_view(), name="index"),
]
