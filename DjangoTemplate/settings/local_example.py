from DjangoTemplate.settings.default import ALLOWED_HOSTS, BASE_DIR, MIDDLEWARE, INSTALLED_APPS


DEBUG = True


ALLOWED_HOSTS.extend(
    [
        "localhost",
        "127.0.0.1",
    ]
)

# Toolbar requirements.
MIDDLEWARE.append(
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)
INSTALLED_APPS.extend(
    [
        "debug_toolbar",
        "django_extensions",
    ]
)
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar_user_switcher.panels.UserPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",

]
INSTALLED_APPS.append("django_extensions")




# Local Email

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'