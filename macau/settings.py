import os
from pathlib import Path

import django_stubs_ext
import environ

django_stubs_ext.monkeypatch()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "super-secret-key"),
    ALLOWED_HOSTS=(list, ["*"]),
    TEST=(bool, False),
    ROOT_REDIRECT_URL=(str, ""),
    TZ=(str, "UTC"),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

TEST = env("TEST")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.humanize",
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "health_check",
    "health_check.db",
    "macau",
    "macau.users",
    "macau.redirects",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "macau.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "macau.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {"default": env.db_url(default="sqlite:///" + str(BASE_DIR / "db.sqlite3"))}

if "sqlite" in DATABASES["default"]["ENGINE"]:
    db_init_command = f"""
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    PRAGMA temp_store=MEMORY;
    PRAGMA auto_vacuum=INCREMENTAL;
    PRAGMA busy_timeout=10000;
    PRAGMA threads={os.cpu_count()};
    PRAGMA secure_delete=OFF;
    PRAGMA mmap_size=50000000;
    PRAGMA cache_size=-262144;
    """
    DATABASES["default"]["OPTIONS"] = {"init_command": db_init_command}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = env("TZ")

USE_I18N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "collected-static"
WHITENOISE_ALLOW_ALL_ORIGINS = False
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "formatters": {
        "verbose": {
            # Mostly copied from gunicorn
            "format": "%(asctime)s [%(process)d] [%(name)s] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "CRITICAL" if TEST else "INFO",
            "propagate": False,
        },
        "macau": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

HEALTH_CHECK = {"DISABLE_THREADING": True}

PERMISSIONS_POLICY: dict[str, list] = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ROOT_REDIRECT_URL = env("ROOT_REDIRECT_URL")
