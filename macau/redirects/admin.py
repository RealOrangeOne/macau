from .models import Redirect
from macau.admin import admin_site
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.text import Truncator


@admin.register(Redirect, site=admin_site)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ["slug", "view_destination", "is_permanent"]
    search_fields = ["slug", "destination"]
    list_filter = ["is_permanent"]
    ordering = ["slug"]

    readonly_fields = ["created_at", "modified_at"]

    fieldsets = (
        (None, {"fields": ("slug",)}),
        (_("Response"), {"fields": ("destination", "is_permanent")}),
        (_("Metadata"), {"fields": ("created_at", "modified_at")}),
    )

    @admin.display(description="Destination")
    def view_destination(self, obj: Redirect) -> str:
        truncated_url = Truncator(obj.destination).chars(50)
        return format_html("<a href='{}'>{}</a>", obj.destination, truncated_url)
