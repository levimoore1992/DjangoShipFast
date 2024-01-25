# pylint: disable=duplicate-code

from django_template.settings.default import *  # noqa: F401,F403

ALLOWED_HOSTS.extend(
    [
        "localhost",
        "127.0.0.1",
    ]
)

# Toolbar requirements.
MIDDLEWARE.extend(
    [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "hijack.middleware.HijackUserMiddleware",
    ]
)
INSTALLED_APPS.extend(
    ["debug_toolbar", "django_extensions", "hijack", "hijack.contrib.admin"]
)
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "django_template.dev_utils.ReplaceImagesPanel",
]


# Local Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "admin@localhost"


LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

# For django hijack to redirect home after hijacking
LOGIN_REDIRECT_URL = "/"
