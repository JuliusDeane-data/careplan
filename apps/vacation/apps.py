from django.apps import AppConfig


class VacationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vacation'

    def ready(self):
        """Import signals when app is ready."""
        import apps.vacation.signals  # noqa
