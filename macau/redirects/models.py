from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Redirect(models.Model):
    slug = models.SlugField(_("slug"))

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    destination = models.URLField(_("destination"))

    is_permanent = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.slug

    def get_absolute_url(self) -> str:
        return reverse("redirects:redirect", args=[self.slug])
