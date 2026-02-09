from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.api.organization"

    def ready(self):
        import app.api.permissions  # registers rules
