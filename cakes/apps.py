from django.apps import AppConfig

class CakesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cakes'
    
    def ready(self):
        # Import signals here to ensure they are loaded
        import cakes.signals