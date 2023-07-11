from DjangoTemplate.settings.default import *  # noqa: F401,F403

try:
    from DjangoTemplate.settings.local import *  # noqa: F401,F403
except ImportError:
    pass