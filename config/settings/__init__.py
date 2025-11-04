"""
Settings package for Careplan project.

Automatically imports the correct settings module based on DJANGO_ENV environment variable.
Defaults to development settings if not specified.
"""

import os

# Determine which settings to use
env = os.getenv('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'development':
    from .development import *
else:
    from .base import *
