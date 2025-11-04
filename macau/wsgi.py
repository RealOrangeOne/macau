import os

from django.core.wsgi import get_wsgi_application
from granian.utils.proxies import wrap_wsgi_with_proxy_headers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "macau.settings")

application = wrap_wsgi_with_proxy_headers(get_wsgi_application(), trusted_hosts="*")
