from django.apps import AppConfig


class AppauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appauth'

    def ready(self):
        import appauth.signals
