"""
Django settings for tilavarauspalvelu project.

Generated by 'django-admin startproject' using Django 3.0.10.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import logging
import os
import subprocess

import environ
import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

from tilavarauspalvelu.loggers import LOGGING_CONSOLE, LOGGING_ELASTIC

logger = logging.getLogger("settings")


def get_git_revision_hash() -> str:
    """
    Retrieve the git hash for the underlying git repository or die trying
    We need a way to retrieve git revision hash for sentry reports
    I assume that if we have a git repository available we will
    have git-the-comamand as well
    """
    try:
        # We are not interested in gits complaints
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, encoding="utf8"
        )
    # ie. "git" was not found
    # should we return a more generic meta hash here?
    # like "undefined"?
    except FileNotFoundError:
        git_hash = "git_not_available"
    except subprocess.CalledProcessError:
        # Ditto
        git_hash = "no_repository"
    return git_hash.rstrip()


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "graphene_django",
    "rest_framework",
    "drf_spectacular",
    "resources",
    "spaces",
    "reservations",
    "services",
    "reservation_units",
    "api",
    "applications",
    "opening_hours",
    "allocation",
    "django_extensions",
    "mptt",
    "django_filters",
    "corsheaders",
    "auditlog",
    "elasticapm.contrib.django",
    "modeltranslation",
    "django.contrib.gis",
    "permissions",
    "users",
    "social_django",
    "tinymce",
    "easy_thumbnails",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "tilavarauspalvelu.urls"

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
                "helusers.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "tilavarauspalvelu.wsgi.application"


root = environ.Path(BASE_DIR)

env = environ.Env(
    DEBUG=(bool, False),
    DJANGO_LOG_LEVEL=(str, "DEBUG"),
    CONN_MAX_AGE=(int, 0),
    DATABASE_URL=(str, "sqlite:../db.sqlite3"),
    TOKEN_AUTH_ACCEPTED_AUDIENCE=(str, ""),
    TOKEN_AUTH_SHARED_SECRET=(str, ""),
    SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),
    ADMINS=(list, []),
    SECURE_PROXY_SSL_HEADER=(tuple, None),
    MEDIA_ROOT=(environ.Path(BASE_DIR), root("media")),
    STATIC_ROOT=(environ.Path(BASE_DIR), root("staticroot")),
    MEDIA_URL=(str, "/media/"),
    STATIC_URL=(str, "/static/"),
    TRUST_X_FORWARDED_HOST=(bool, True),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, "development"),
    MAIL_MAILGUN_KEY=(str, ""),
    MAIL_MAILGUN_DOMAIN=(str, ""),
    MAIL_MAILGUN_API=(str, ""),
    RESOURCE_DEFAULT_TIMEZONE=(str, "Europe/Helsinki"),
    CORS_ALLOWED_ORIGINS=(list, []),
    ELASTIC_APM_SERVER_URL=(str, None),
    ELASTIC_APM_SERVICE_NAME=(str, None),
    ELASTIC_APM_SECRET_TOKEN=(str, None),
    AUDIT_LOGGING_ENABLED=(bool, False),
    TMP_PERMISSIONS_DISABLED=(bool, False),
    TUNNISTAMO_JWT_AUDIENCE=(str, "https://api.hel.fi/auth/tilavarausapidev"),
    TUNNISTAMO_JWT_ISSUER=(str, "https://api.hel.fi/sso/openid"),
    TUNNISTAMO_ADMIN_KEY=(str, "tilanvaraus-django-admin-dev"),
    TUNNISTAMO_ADMIN_SECRET=(str, None),
    TUNNISTAMO_ADMIN_OIDC_ENDPOINT=(str, "https://api.hel.fi/sso/openid/"),
    IPWARE_META_PRECEDENCE_ORDER=(str, "HTTP_X_FORWARDED_FOR"),
    HAUKI_API_URL=(str, None),
    HAUKI_ORIGIN_ID=(str, "tvp"),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

environ.Env.read_env()

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
DEBUG = env("DEBUG")
TMP_PERMISSIONS_DISABLED = env("TMP_PERMISSIONS_DISABLED")

LOGGING = LOGGING_ELASTIC if env("ELASTIC_APM_SERVER_URL") else LOGGING_CONSOLE

# Database configuration
DATABASES = {"default": env.db()}
DATABASES["default"]["CONN_MAX_AGE"] = env("CONN_MAX_AGE")

# SECURITY WARNING: keep the secret key used in production secret!
# Using hard coded in dev environments if not defined.
if DEBUG is True and env("SECRET_KEY") == "":
    logger.warning(
        "Running in debug mode without proper secret key. Fix if not intentional"
    )
    SECRET_KEY = "example_secret"
else:
    SECRET_KEY = env("SECRET_KEY")

ADMINS = env("ADMINS")

SECURE_PROXY_SSL_HEADER = env("SECURE_PROXY_SSL_HEADER")

# Static files (CSS, JavaScript, Images) and media uploads
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = env("STATIC_ROOT")
MEDIA_ROOT = env("MEDIA_ROOT")

STATIC_URL = env("STATIC_URL")
MEDIA_URL = env("MEDIA_URL")

HAUKI_API_URL = env("HAUKI_API_URL")
HAUKI_ORIGIN_ID = env("HAUKI_ORIGIN_ID")


RESERVATION_UNIT_IMAGES_ROOT = "reservation_unit_images"

# Whether to trust X-Forwarded-Host headers for all purposes
# where Django would need to make use of its own hostname
# fe. generating absolute URLs pointing to itself
# Most often used in reverse proxy setups
USE_X_FORWARDED_HOST = env("TRUST_X_FORWARDED_HOST")

# Configure cors
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

AUDIT_LOGGING_ENABLED = env("AUDIT_LOGGING_ENABLED")

# Configure sentry
if env("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        environment=env("SENTRY_ENVIRONMENT"),
        release=get_git_revision_hash(),
        integrations=[DjangoIntegration()],
    )

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "fi"
LANGUAGES = (("fi", _("Finnish")), ("en", _("English")), ("sv", _("Swedish")))

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "helusers.tunnistamo_oidc.TunnistamoOIDCAuth",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/"

SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

OIDC_API_TOKEN_AUTH = {
    "AUDIENCE": env("TUNNISTAMO_JWT_AUDIENCE"),
    "ISSUER": env("TUNNISTAMO_JWT_ISSUER"),
}

SOCIAL_AUTH_TUNNISTAMO_KEY = env("TUNNISTAMO_ADMIN_KEY")
SOCIAL_AUTH_TUNNISTAMO_SECRET = env("TUNNISTAMO_ADMIN_SECRET")
SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = env("TUNNISTAMO_ADMIN_OIDC_ENDPOINT")
IPWARE_META_PRECEDENCE_ORDER = ("HTTP_X_FORWARDED_FOR",)

GRAPHENE = {"SCHEMA": "api.graphql.schema.schema"}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["permissions.api_permissions.ReadOnly"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["helusers.oidc.ApiTokenAuthentication"]
    + (
        [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ]
        if DEBUG
        else []
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
SPECTACULAR_SETTINGS = {
    # path prefix is used for tagging the discovered operations.
    # use '/api/v[0-9]' for tagging apis like '/api/v1/albums' with ['albums']
    "SCHEMA_PATH_PREFIX": r"/v[^/]",
    "TITLE": "Tilavaraus API",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "TAGS": [
        {
            "name": "openapi",
            "description": "",
        },
        {
            "name": "application",
            "description": "Applications for recurring reservations for individuals and organisations.",
        },
        {
            "name": "application_event",
            "description": "Single recurring events related to a certain application.",
        },
        {
            "name": "application_round",
            "description": "Information of past, current and future application periods "
            "to where applications are targeted to.",
        },
        {
            "name": "parameters",
            "description": "",
        },
        {
            "name": "reservation",
            "description": "Reservation for single or multiple reservation units.",
        },
        {
            "name": "reservation_unit",
            "description": "A single unit that can be reserved. "
            "Wrapper for combinations of spaces, resources and services.",
        },
    ],
}


THUMBNAIL_ALIASES = {
    "": {
        "small": {"size": (250, 250), "crop": True},
        "medium": {"size": (384, 384), "crop": True},
    },
}


# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
local_settings_path = os.path.join(BASE_DIR, "local_settings.py")
if os.path.exists(local_settings_path):
    with open(local_settings_path) as fp:
        code = compile(fp.read(), local_settings_path, "exec")
    exec(code, globals(), locals())

if TMP_PERMISSIONS_DISABLED and not DEBUG:
    logging.error("Running with permissions disabled in production environment.")

if not all(
    [
        OIDC_API_TOKEN_AUTH["AUDIENCE"],
        OIDC_API_TOKEN_AUTH["ISSUER"],
        SOCIAL_AUTH_TUNNISTAMO_KEY,
        SOCIAL_AUTH_TUNNISTAMO_SECRET,
        SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT,
    ]
):
    logging.error(
        "Some of Tunnistamo environment variables are not set. Authentication may not work properly!"
    )
