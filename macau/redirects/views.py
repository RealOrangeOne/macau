from django.views import View
from django.http import HttpRequest, HttpResponse
from django import shortcuts
from .models import Redirect
from django.utils.decorators import method_decorator
from django.views.decorators.common import no_append_slash


class RedirectView(View):
    @method_decorator(no_append_slash)
    def dispatch(self, request: HttpRequest, slug: str) -> HttpResponse:
        redirect = shortcuts.get_object_or_404(Redirect, slug=slug)

        return shortcuts.redirect(
            redirect.destination, permanent=redirect.is_permanent, preserve_request=True
        )
