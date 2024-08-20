"""
Django settings for django_template project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "FALSE").upper() == "TRUE"

# This is in case a user types in the http:// url domain. It will redirect to the https:// version
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "FALSE").upper() == "TRUE"

# Version of Application
VERSION = os.getenv("VERSION")

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "django_recaptcha",  # Google Captcha
    "waffle",  # Feature Flags
    "django_ckeditor_5",
    "django_htmx",
    "admin_sso",  # google login for admin
    # celery apps
    "django_celery_beat",
    "django_celery_results",
    # project apps
    "apps.main",
    "apps.users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "apps.users.middleware.TrackUserIPAndDeviceMiddleware",
    "apps.main.middleware.HTMXExceptionMiddleware",
]

ROOT_URLCONF = "django_template.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],  # templates directory is in root directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.main.context_processors.report_form",
                "apps.main.context_processors.notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "django_template.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASS"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {"sslmode": os.getenv("DATABASE_SSLMODE", "disable")},
        "ATOMIC_REQUESTS": True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DATE_FORMAT = "j/n/y"  # Day/Month/Year without leading zeros.
TIME_FORMAT = "P"  # Hour in 12-hour format with AM/PM.
DATETIME_FORMAT = "P j/n/y"  # Combination of both time and date.

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Sentry variables
ENABLE_SENTRY = os.environ.get("ENABLE_SENTRY", "TRUE").upper() == "TRUE"

SENTRY_DSN = os.getenv("SENTRY_DSN")

SENTRY_ENV = os.getenv("SENTRY_ENV", "unknown")

LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "admin": {  # for loggers in the admin
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

STRIPE_API_PK = os.getenv("STRIPE_PK_KEY")
STRIPE_API_SK = os.getenv("STRIPE_SK_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# Authentication settings

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # Default backend
    "apps.users.auth.DjangoAdminAuthBackend",
)

DJANGO_ADMIN_SSO_OAUTH_CLIENT_ID = os.getenv("DJANGO_ADMIN_SSO_OAUTH_CLIENT_ID")
DJANGO_ADMIN_SSO_OAUTH_CLIENT_SECRET = os.getenv("DJANGO_ADMIN_SSO_OAUTH_CLIENT_SECRET")

# We use our own template, don't add the admin_sso login button
DJANGO_ADMIN_SSO_ADD_LOGIN_BUTTON = False

LOGIN_URL = "login"

# settings.py
CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True  # needed for django-celery results

# Google Captcha Settings
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY")
# Silencing the error below because we intentionally use the test keys in development
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

# Hosted Email Settings

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# DigitalOcean Spaces settings
AWS_ACCESS_KEY_ID = os.getenv("DIGITAL_OCEAN_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("DIGITAL_OCEAN_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("DIGITAL_OCEAN_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_DEFAULT_ACL = "public-read"
# Tell Django to use S3 to store media files
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
AWS_QUERYSTRING_AUTH = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# CK Editor Config
CKEDITOR_5_FILE_STORAGE = MEDIA_URL
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "ckeditor_upload"
