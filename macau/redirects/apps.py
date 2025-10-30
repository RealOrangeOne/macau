from django.apps import AppConfig


class RedirectsConfig(AppConfig):
    name = "macau.redirects"
    label = "redirects"
    verbose_name = "Redirects"

    def ready(self) -> None:
        from . import admin  # noqa: F401
