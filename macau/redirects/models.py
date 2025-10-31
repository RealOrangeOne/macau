from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Redirect(models.Model):
    slug = models.SlugField(_("slug"), primary_key=True)

    is_enabled = models.BooleanField(_("enabled"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    destination = models.URLField(_("destination"))

    is_permanent = models.BooleanField(default=False)

    # NB: It's intentional that these are stored as plain-text
    basic_auth_username = models.CharField(max_length=64, blank=True)
    basic_auth_password = models.CharField(max_length=64, blank=True)

    def __str__(self) -> str:
        return self.slug

    def get_absolute_url(self) -> str:
        return reverse("redirects:redirect", args=[self.slug])
