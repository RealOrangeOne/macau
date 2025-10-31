from base64 import b64encode

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .models import Redirect
from .utils import check_basic_auth


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
        self.assertEqual(response.headers["X-Robots-Tag"], "noindex")
        self.assertIn("no-cache", response.headers["Cache-Control"])

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
            slug="disabled",
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


class RedirectCreateViewTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_superuser("user", "user@example.com", "password")

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_redirect_to_create(self) -> None:
        response = self.client.get("/https://example.com", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add redirect")

        self.assertEqual(
            response.context["adminform"].form.initial,
            {"destination": "https://example.com"},
        )

    def test_unauthenticated(self) -> None:
        self.client.logout()
        response = self.client.get("/https://example.com")
        self.assertEqual(response.status_code, 404)


class RedirectAdminTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_superuser("user", "user@example.com", "password")

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_add_view(self) -> None:
        response = self.client.get(reverse("admin:redirects_redirect_add"))
        self.assertEqual(response.status_code, 200)

    def test_change_view(self) -> None:
        redirect = Redirect.objects.create(
            slug="disabled",
            destination="https://example.com",
        )
        response = self.client.get(
            reverse("admin:redirects_redirect_change", args=[redirect.slug])
        )
        self.assertEqual(response.status_code, 200)


class RootRedirectViewTestCase(SimpleTestCase):
    @override_settings(ROOT_REDIRECT_URL="https://example.com")
    def test_custom_root_redirect_url(self) -> None:
        response = self.client.get("/")
        self.assertRedirects(
            response, "https://example.com", fetch_redirect_response=False
        )
        self.assertEqual(response.headers["X-Robots-Tag"], "noindex")
        self.assertIn("no-cache", response.headers["Cache-Control"])

    @override_settings(ROOT_REDIRECT_URL="admin")
    def test_redirect_root_to_admin(self) -> None:
        response = self.client.get("/")
        self.assertRedirects(
            response, reverse("admin:index"), fetch_redirect_response=False
        )
        self.assertEqual(response.headers["X-Robots-Tag"], "noindex")
        self.assertIn("no-cache", response.headers["Cache-Control"])

    @override_settings(ROOT_REDIRECT_URL="")
    def test_no_root_redirect_url(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)
