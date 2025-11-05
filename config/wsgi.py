"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Ensure logs dir exists before Django configures logging. Use the project
# root (parent of the config package) as the BASE_DIR equivalent.
try:
    log_dir = Path(__file__).resolve().parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    # If creation fails, let Django raise the error when it attempts to open
    # the log file.
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
