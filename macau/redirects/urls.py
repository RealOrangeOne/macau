from django.urls import path, re_path

from django.core.validators import URLValidator

from .views import HandleRedirectView, RedirectCreateView, RootRedirectView

app_name = "redirects"

urlpatterns = [
    path("<slug:slug>", HandleRedirectView.as_view(), name="redirect"),
    # Duplicate the URL definition to allow for optional trailing slash
    path("<slug:slug>/", HandleRedirectView.as_view()),
    re_path(
        f"({URLValidator.regex.pattern})",  # type: ignore[union-attr]
        RedirectCreateView.as_view(),
        name="create",
    ),
    path("", RootRedirectView.as_view(), name="index"),
]
