from .models import Redirect
from macau.admin import admin_site
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.text import Truncator
from django import forms


class RedirectAdminForm(forms.ModelForm):
    def clean(self) -> dict:
        cleaned_data: dict = super().clean()  # type: ignore[assignment]

        if (
            cleaned_data["basic_auth_username"]
            and not cleaned_data["basic_auth_password"]
        ):
            raise forms.ValidationError(
                {
                    "basic_auth_username": "Password must be specified (or only specified) when using basic auth"
                }
            )

        return cleaned_data


@admin.register(Redirect, site=admin_site)
class RedirectAdmin(admin.ModelAdmin):
    form = RedirectAdminForm

    list_display = ["slug", "view_destination", "is_permanent", "view_requires_auth"]
    search_fields = ["slug", "destination"]
    list_filter = ["is_permanent"]
    ordering = ["slug"]

    readonly_fields = ["created_at", "modified_at"]

    fieldsets = (
        (None, {"fields": ("slug",)}),
        (_("Response"), {"fields": ("destination", "is_permanent")}),
        (
            _("Authentication"),
            {
                "classes": ["collapse"],
                "fields": ("basic_auth_username", "basic_auth_password"),
            },
        ),
        (_("Metadata"), {"fields": ("created_at", "modified_at")}),
    )

    @admin.display(description="Destination")
    def view_destination(self, obj: Redirect) -> str:
        truncated_url = Truncator(obj.destination).chars(50)
        return format_html("<a href='{}'>{}</a>", obj.destination, truncated_url)

    @admin.display(description="Requires Auth?", boolean=True)
    def view_requires_auth(self, obj: Redirect) -> bool:
        return bool(obj.basic_auth_password)
