from copy import deepcopy

from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import Truncator
from import_export.admin import ImportExportActionModelAdmin
from import_export.resources import ModelResource

from macau.core.admin import admin_site

from .models import Redirect


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


class RedirectResource(ModelResource):
    class Meta:
        model = Redirect


@admin.register(Redirect, site=admin_site)
class RedirectAdmin(ImportExportActionModelAdmin):
    form = RedirectAdminForm

    resource_classes = [RedirectResource]
    show_change_form_export = False

    list_display = [
        "slug",
        "view_destination",
        "is_enabled",
        "created_at",
    ]
    search_fields = ["slug", "destination"]
    list_filter = ["is_permanent", "is_enabled"]
    ordering = ["slug"]

    readonly_fields = ["created_at", "modified_at", "view_qrcode"]

    fieldsets_dict = {
        None: {"fields": ("slug", "is_enabled")},
        "Response": {"fields": ("destination", "is_permanent")},
        "Authentication": {
            "classes": ["collapse"],
            "fields": ("basic_auth_username", "basic_auth_password"),
        },
        "Metadata": {"fields": ("created_at", "modified_at", "view_qrcode")},
    }

    @admin.display(description="Destination")
    def view_destination(self, obj: Redirect) -> str:
        truncated_url = Truncator(obj.destination).chars(50)
        return format_html("<a href='{}'>{}</a>", obj.destination, truncated_url)

    @admin.display(description="QR Code")
    def view_qrcode(self, obj: Redirect) -> str:
        return format_html(
            "<img src='{}' class='redirect-qrcode' />",
            reverse("redirects:qrcode-png", args=[obj.slug]),
        )

    def get_fieldsets(self, request: HttpRequest, obj: Redirect | None = None) -> list:
        if not obj:
            add_fieldsets: dict = deepcopy(self.fieldsets_dict)

            # Hide metadata, since there won't be any
            del add_fieldsets["Metadata"]

            # Don't collapse authentication fields
            add_fieldsets["Authentication"]["classes"].remove("collapse")

            return list(add_fieldsets.items())
        return list(self.fieldsets_dict.items())
