from django.test import TestCase, SimpleTestCase, RequestFactory
from .models import Redirect
from django.urls import reverse
from base64 import b64encode
from .utils import check_basic_auth
from django.http import HttpRequest


class RedirectViewTestCase(TestCase):
    def test_accessible(self) -> None:
        redirect = Redirect.objects.create(
            slug="test", destination="https://example.com"
        )

        with self.assertNumQueries(1):
            response = self.client.get(
                reverse("redirects:redirect", args=[redirect.slug])
            )

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["Location"], redirect.destination)

    def test_trailing_slash_optional(self) -> None:
        redirect = Redirect.objects.create(
            slug="test", destination="https://example.com"
        )

        for url_suffix in ["", "/"]:
            with self.subTest(url_suffix=url_suffix):
                response = self.client.get(f"/{redirect.slug}{url_suffix}")
                self.assertEqual(response.status_code, 307)
                self.assertEqual(response.headers["Location"], redirect.destination)

    def test_permanent_redirect(self) -> None:
        for is_permanent in [True, False]:
            with self.subTest(is_permanent=is_permanent):
                redirect = Redirect.objects.create(
                    slug=f"test-{is_permanent}",
                    destination="https://example.com",
                    is_permanent=is_permanent,
                )

                response = self.client.get(
                    reverse("redirects:redirect", args=[redirect.slug])
                )

                self.assertEqual(response.status_code, 308 if is_permanent else 307)
                self.assertEqual(response.headers["Location"], redirect.destination)

    def test_unknown_slug(self) -> None:
        response = self.client.get(reverse("redirects:redirect", args=["unknown"]))
        self.assertEqual(response.status_code, 404)

    def test_basic_auth(self) -> None:
        redirect = Redirect.objects.create(
            slug="basic",
            destination="https://example.com",
            basic_auth_username="username",
            basic_auth_password="password",
        )

        response = self.client.get(reverse("redirects:redirect", args=[redirect.slug]))
        self.assertEqual(response.status_code, 401)

        response = self.client.get(
            reverse("redirects:redirect", args=[redirect.slug]),
            headers={
                "Authorization": f"Basic {b64encode(b'username:password').decode()}"
            },
        )
        self.assertEqual(response.status_code, 307)

        response = self.client.get(
            reverse("redirects:redirect", args=[redirect.slug]),
            headers={"Authorization": f"Basic {b64encode(b'password').decode()}"},
        )
        self.assertEqual(response.status_code, 401)

    def test_cant_access_disabled_redirect(self) -> None:
        redirect = Redirect.objects.create(
            slug="basic",
            destination="https://example.com",
        )

        response = self.client.get(reverse("redirects:redirect", args=[redirect.slug]))
        self.assertEqual(response.status_code, 307)

        redirect.is_enabled = False
        redirect.save()

        response = self.client.get(reverse("redirects:redirect", args=[redirect.slug]))
        self.assertEqual(response.status_code, 404)


class CheckBasicAuthTestCase(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def _get_request(self, credentials: str) -> HttpRequest:
        return self.factory.get(
            "/",
            headers={
                "Authorization": "Basic " + b64encode(credentials.encode()).decode()
            },
        )

    def test_no_header(self) -> None:
        self.assertFalse(
            check_basic_auth(self.factory.get("/"), "username", "password")
        )

    def test_wrong_credentials(self) -> None:
        self.assertFalse(
            check_basic_auth(self._get_request("wrong:wrong"), "username", "password")
        )

    def test_correct_credentials(self) -> None:
        self.assertTrue(
            check_basic_auth(
                self._get_request("username:password"), "username", "password"
            )
        )

    def test_missing_credentials(self) -> None:
        self.assertFalse(
            check_basic_auth(
                self.factory.get("/", headers={"Authorization": "Basic"}),
                "username",
                "password",
            )
        )

    def test_multiple_credentials(self) -> None:
        credentials = b64encode(b"username:password").decode()
        self.assertTrue(
            check_basic_auth(
                self.factory.get(
                    "/",
                    headers={
                        "Authorization": f"Basic {credentials}, Basic {credentials}"
                    },
                ),
                "username",
                "password",
            )
        )

    def test_not_base64(self) -> None:
        self.assertFalse(
            check_basic_auth(
                self.factory.get(
                    "/",
                    headers={"Authorization": "Basic mypassword"},
                ),
                "username",
                "password",
            )
        )
