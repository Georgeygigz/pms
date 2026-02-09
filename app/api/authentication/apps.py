from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.api.authentication"

    def ready(self):
          import app.api.authentication.signals
          import app.api.authentication.schema
