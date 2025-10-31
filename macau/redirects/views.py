from django.views import View
from django.views.generic import RedirectView
from django.http import HttpRequest, HttpResponse, Http404
from django import shortcuts
from .models import Redirect
from django.utils.decorators import method_decorator
from django.views.decorators.common import no_append_slash
from .utils import check_basic_auth
from django.utils.cache import add_never_cache_headers
from urllib.parse import urlencode
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import Any


class HandleRedirectView(View):
    def _handle_redirect(
        self, request: HttpRequest, redirect: Redirect
    ) -> HttpResponse:
        if redirect.basic_auth_password:
            if not check_basic_auth(
                request, redirect.basic_auth_username, redirect.basic_auth_password
            ):
                return HttpResponse(
                    status=401,
                    content="Authentication required",
                    headers={"WWW-Authenticate": "Basic"},
                    content_type="text/plain",
                )

        return shortcuts.redirect(
            redirect.destination,
            permanent=redirect.is_permanent,
            preserve_request=True,
        )

    @method_decorator(no_append_slash)
    def dispatch(self, request: HttpRequest, slug: str) -> HttpResponse:
        redirect = shortcuts.get_object_or_404(Redirect, slug=slug, is_enabled=True)

        response = self._handle_redirect(request, redirect)

        # Prevent the redirect from being cached
        add_never_cache_headers(response)

        # Prevent search engines from indexing redirects
        response.headers["X-Robots-Tag"] = "noindex"

        return response


class RedirectCreateView(LoginRequiredMixin, RedirectView):
    http_method_names = ["get"]

    def get_redirect_url(self, url: str, *args: Any, **kwargs: Any) -> str:
        return (
            reverse("admin:redirects_redirect_add")
            + "?"
            + urlencode({"destination": url})
        )

    def handle_no_permission(self) -> None:  # type: ignore[override]
        raise Http404
