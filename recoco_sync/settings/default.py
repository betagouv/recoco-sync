from __future__ import annotations

from pathlib import Path

import sentry_sdk
from environ import Env
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
ENVIRONMENT = env.str("ENVIRONMENT", default="dev")

dotenv_file = Path(env.str("DOTENV_FILE", default=BASE_DIR / ".." / ".env"))
if ENVIRONMENT != "testing" and dotenv_file.exists():
    env.read_env(dotenv_file)

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
ROOT_URLCONF = "recoco_sync.urls"
WSGI_APPLICATION = "recoco_sync.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#
# Static files
#
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

#
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
#
LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

#
# Application definition
#
INSTALLED_APPS = (
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    + [
        "django_celery_results",
        "django_extensions",
    ]
    + [
        "recoco_sync.main",
        "recoco_sync.grist_connector",
    ]
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

#
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
DATABASES = {"default": env.db()}

#
# Authentication
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
#
AUTH_USER_MODEL = "main.User"

#
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
#
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#
# Storages
#
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

#
# Celery Configuration Options
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
#
CELERY_TIMEZONE = "Europe/Paris"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = env.str("BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ALWAYS_EAGER = env.bool("CELERY_ALWAYS_EAGER", default=False)
CELERY_RESULT_BACKEND = "django-db"

#
# Webhook security
#
WEBHOOK_SECRET = env.str("WEBHOOK_SECRET")

#
# Recoco API congiguration
#
RECOCO_API_USERNAME = env.str("RECOCO_API_USERNAME")
RECOCO_API_PASSWORD = env.str("RECOCO_API_PASSWORD")

#
# Sentry
#
if SENTRY_URL := env.str("SENTRY_URL", default=None):
    sentry_sdk.init(
        dsn=SENTRY_URL,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment=ENVIRONMENT,
        traces_sample_rate=0.05,
        send_default_pii=True,
    )

#
# Grist
#

TABLE_COLUMN_HEADER_MAX_LENGTH = env.str("TABLE_COLUMN_HEADER_MAX_LENGTH", default=80)
