from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from typing import Any

from macau.admin import admin_site


@admin.register(User, site=admin_site)
class UserAdmin(BaseUserAdmin):
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Group, site=admin_site)
class GroupAdmin(BaseGroupAdmin):
    def formfield_for_manytomany(
        self, db_field: Any, request: Any, **kwargs: Any
    ) -> Any:
        if db_field.name == "permissions":
            allowed_content_types = ContentType.objects.get_for_models(
                User, Group
            ).values()
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            kwargs["queryset"] = qs.filter(content_type__in=allowed_content_types)
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)
