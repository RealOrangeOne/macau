from typing import TYPE_CHECKING, Any

from django.apps import AppConfig
from django.db.models.signals import pre_save

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class UsersConfig(AppConfig):
    name = "macau.users"
    label = "users"
    verbose_name = "Users"

    def ready(self) -> None:
        from django.contrib.auth.models import User

        from . import admin  # noqa: F401

        pre_save.connect(self.pre_user_save, User)

    def pre_user_save(
        self, sender: type["User"], instance: "User", **kwargs: Any
    ) -> None:
        # Force users to be staff (not much use otherwise)
        instance.is_staff = True
