from restaurant.settings import *  # NOQA
import os
import json
import dj_database_url

DATABASES["default"] = dj_database_url.config()
DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"
DATABASES["default"]["CONN_MAX_AGE"] = 60
DATABASES["default"]["ATOMIC_REQUESTS"] = True

DEBUG = os.getenv("DEBUG") == "True"

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

ADMINS = [(os.getenv("ADMIN_NAME"), os.getenv("ADMIN_EMAIL"))]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "strict-origin"

SERVER_EMAIL = os.getenv("SERVER_EMAIL")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

CSRF_TRUSTED_ORIGINS = [os.getenv("CSRF_TRUSTED_ORIGINS")]


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv("SENDGRID_SERVER")
EMAIL_HOST_USER = os.getenv("SENDGRID_USERNAME")
EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_PASSWORD")
EMAIL_PORT = os.getenv("SENDGRID_PORT")
EMAIL_TIMEOUT = 500
EMAIL_USE_SSL = False
EMAIL_SUBJECT_PREFIX = "[Restaurant API] "
