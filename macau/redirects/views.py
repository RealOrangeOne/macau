from typing import Any

import qrcode
import qrcode.image.svg
from django import shortcuts
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.common import no_append_slash
from django.views.generic import RedirectView

from .models import Redirect
from .utils import check_basic_auth


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

        redirect_class = (
            HttpResponsePermanentRedirect
            if redirect.is_permanent
            else HttpResponseRedirect
        )

        return redirect_class(redirect.destination, preserve_request=True)

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
        return reverse("admin:redirects_redirect_add", query={"destination": url})

    def handle_no_permission(self) -> None:  # type: ignore[override]
        raise Http404


class RootRedirectView(RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str:
        if redirect_url := settings.ROOT_REDIRECT_URL:
            if redirect_url == "admin":
                return reverse("admin:index")
            return redirect_url  # type: ignore[no-any-return]
        raise Http404

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        response = super().dispatch(request, *args, **kwargs)

        # Prevent the redirect from being cached
        add_never_cache_headers(response)

        # Prevent search engines from indexing redirects
        response.headers["X-Robots-Tag"] = "noindex"

        return response


class RedirectQRCodeView(View):
    CONTENT_TYPE = {"svg": "image/svg+xml", "png": "image/png"}

    @method_decorator(no_append_slash)
    def get(self, request: HttpRequest, slug: str, image_format: str) -> HttpResponse:
        redirect = shortcuts.get_object_or_404(Redirect, slug=slug, is_enabled=True)

        data = request.build_absolute_uri(redirect.get_absolute_url())

        match image_format:
            case "png":
                qr = qrcode.QRCode(border=0, box_size=1)
                qr.add_data(data)
                img = qr.make_image(back_color="transparent")
            case "svg":
                qr = qrcode.QRCode(
                    border=0, image_factory=qrcode.image.svg.SvgPathImage
                )
                qr.add_data(data)
                img = qr.make_image(back_color="transparent")
            case _:
                return HttpResponse("Unknown format", status=400)

        response = HttpResponse(content_type=self.CONTENT_TYPE[image_format])
        img.save(response)
        patch_cache_control(response, max_age=300)
        return response
