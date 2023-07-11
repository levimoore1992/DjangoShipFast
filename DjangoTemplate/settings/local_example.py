from DjangoTemplate.settings.default import ALLOWED_HOSTS, BASE_DIR, MIDDLEWARE, INSTALLED_APPS


DEBUG = True


ALLOWED_HOSTS.extend(
    [
        # for /virtuoso/ admin only
        "localhost",
        "127.0.0.1",
        "web",
    ]
)

# Local Email

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'