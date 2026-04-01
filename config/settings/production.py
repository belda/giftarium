from config.settings.base import *  # noqa: F401, F403
from decouple import config, Csv

DEBUG = False

# Set CSRF_TRUSTED_ORIGINS to a comma-separated list of trusted origins in .env
# e.g. CSRF_TRUSTED_ORIGINS=https://gifts.example.com,https://www.gifts.example.com
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://darky.blda.cz,https://www.darky.blda.cz",
    cast=Csv(),
)

# Set SECURE_SSL_REDIRECT=False in .env if your reverse proxy handles HTTPS termination
# and forwards plain HTTP to gunicorn (e.g. Traefik, nginx with proxy_pass http://...)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# PostgreSQL — used in Docker; configure DB_* vars in .env
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="giftarium"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Email — configure all EMAIL_* vars in .env
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@darky.blda.cz")

DEFAULT_CURRENCY = "CZK"