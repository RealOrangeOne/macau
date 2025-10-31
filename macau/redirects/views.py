from django.views import View
from django.http import HttpRequest, HttpResponse
from django import shortcuts
from .models import Redirect
from django.utils.decorators import method_decorator
from django.views.decorators.common import no_append_slash
from .utils import check_basic_auth
from django.utils.cache import add_never_cache_headers


class RedirectView(View):
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
