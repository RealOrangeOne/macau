from django.test import TestCase
from .models import Redirect
from django.urls import reverse


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
