from django.urls import path

from .views import RedirectView

app_name = "redirects"

urlpatterns = [
    path("<slug:slug>", RedirectView.as_view(), name="redirect"),
    # Duplicate the URL definition to allow for optional trailing slash
    path("<slug:slug>/", RedirectView.as_view()),
]
