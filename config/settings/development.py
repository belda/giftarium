from config.settings.base import *  # noqa: F401, F403

DEBUG = True

# Show emails in terminal during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
