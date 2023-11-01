from django_template.settings.default import *  # noqa: F401,F403

ALLOWED_HOSTS = ["localhost", "testserver", "127.0.0.1", ".ngrok.io"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "django-test",
        "USER": "django",
        "PASSWORD": "django",
        "HOST": os.environ.get("DB_HOST"),
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
    }
}

SENTRY_ENV = "test_runner"

# This is added here because the tests need to be able to access the media files
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Celery test settings
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
CELERY_TASK_ALWAYS_EAGER = True
