"""
Production settings for Careplan project.
Optimized for security and performance with 100+ concurrent users.
"""

from .base import *

# Debug MUST be False in production
DEBUG = False

# Allowed hosts must be configured via environment variable
# Example: ALLOWED_HOSTS=example.com,www.example.com
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production")


# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Database configuration with optimized connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',  # 30 second query timeout
}


# Static files - use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Logging - Production logging with error reporting
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'

# Add error email handler
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@careplan.com')),
]

LOGGING['handlers']['mail_admins'] = {
    'level': 'ERROR',
    'class': 'django.utils.log.AdminEmailHandler',
    'filters': ['require_debug_false'],
}

LOGGING['loggers']['django']['handlers'].append('mail_admins')


# Email backend - use real SMTP in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# REST Framework - stricter rate limiting in production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '50/hour',
    'user': '500/hour',
    'auth': '5/minute',
}


# Cache - ensure Redis is used
if 'dummy' in CACHES['default']['BACKEND']:
    raise ValueError("Cannot use dummy cache in production")


# CORS - must be explicitly configured
CORS_ALLOW_ALL_ORIGINS = False
if not CORS_ALLOWED_ORIGINS:
    raise ValueError("CORS_ALLOWED_ORIGINS must be set in production")


# Optional: Configure Sentry for error tracking
# SENTRY_DSN = config('SENTRY_DSN', default='')
# if SENTRY_DSN:
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,
#         send_default_pii=False,
#     )
