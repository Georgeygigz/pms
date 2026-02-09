from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.api.maintenance"

    def ready(self):
        import app.api.maintenance.signals

