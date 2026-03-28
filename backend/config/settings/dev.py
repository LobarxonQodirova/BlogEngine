"""
Development-specific Django settings for BlogEngine.

Inherits from base settings and overrides for local development.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend"]

# ---------------------------------------------------------------------------
# Debug toolbar (optional, enable if installed)
# ---------------------------------------------------------------------------
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Email: use console backend in development
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# CORS: allow all origins in development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Cache: use local memory cache in development for speed
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "blogengine-dev-cache",
    }
}

# ---------------------------------------------------------------------------
# Celery: run tasks eagerly for simpler debugging
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = False  # set True to bypass Redis during development

# ---------------------------------------------------------------------------
# Throttling: relax rate limits for development
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "10000/hour",
    "user": "50000/hour",
}

# ---------------------------------------------------------------------------
# Logging: more verbose in development
# ---------------------------------------------------------------------------
LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "WARNING",
    "propagate": False,
}

# ---------------------------------------------------------------------------
# Static files: simpler storage for dev
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
