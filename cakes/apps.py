from django.apps import AppConfig

class CakesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cakes'

    def ready(self):
        import cakes.signals