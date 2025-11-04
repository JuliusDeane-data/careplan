"""
Development settings for Careplan project.
"""

from .base import *

# Debug mode enabled in development
DEBUG = True

# Allowed hosts for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']


# Database - can use PostgreSQL or SQLite for development
# Override with SQLite if you prefer for local development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Email backend - console output for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Django Debug Toolbar
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
]

# For Docker or remote access, also allow any IP to see debug toolbar
import socket
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]
except Exception:
    pass

# Show all SQL queries in debug mode
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'IS_RUNNING_TESTS': False,  # Disable debug toolbar during tests
}


# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True


# Logging - more verbose in development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'


# Disable some security features in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# Cache - use dummy cache for development if you want to disable caching
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
# }
