from webapptemplate.default_settings import *  # noqa: F401, F403

from pathlib import Path
from decouple import config, Csv
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROJECT_NAME = "giftarium"
APP_NAME = "Giftarium"
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Project templates take precedence over package templates
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"] + list(TEMPLATES[0]["DIRS"])

# Project static files alongside package static files
STATICFILES_DIRS = [BASE_DIR / "static"] + [
    d for d in STATICFILES_DIRS if d != BASE_DIR / "static"
]

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@darky.blda.cz")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"

ADMINS = [("Giftarium Admin", config("ADMIN_EMAIL", default="jakub.belda@gmail.com"))]

SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"] = config("GOOGLE_CLIENT_ID", default="")
SOCIALACCOUNT_PROVIDERS["google"]["APP"]["secret"] = config("GOOGLE_CLIENT_SECRET", default="")

LOGIN_REDIRECT_URL = "/gifts/mine/"

# Internationalisation
LANGUAGE_CODE = "cs"
LANGUAGES = [
    ("cs", _("Czech")),
    ("en", _("English")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
    "django.middleware.locale.LocaleMiddleware",
)

# Add your project-specific installed apps here:
INSTALLED_APPS += ["apps.gifts.apps.GiftsConfig"]

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "apps.gifts.context_processors.ws_settings",
]
