#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Ensure runtime logs dir exists before Django configures logging.
    # BASE_DIR in settings points to this file's parent, so create a
    # 'logs' directory next to manage.py to match BASE_DIR / 'logs'.
    try:
        log_dir = Path(__file__).resolve().parent / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If creation fails (permissions, etc.) continue and let Django
        # raise an appropriate error when it tries to open the log file.
        # Avoid importing settings here to prevent triggering logging.
        pass

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
