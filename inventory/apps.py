# inventory/apps.py

from django.apps import AppConfig

class InventoryConfig(AppConfig):
    """
    Configuration for the 'inventory' application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        """
        This method is called by Django when the application registry is fully
        populated and the app is ready. It's the standard place to import
        and connect signals.

        By importing `inventory.signals` here, we ensure that our signal
        handlers (the functions decorated with @receiver) are registered
        and will be triggered when models are saved or deleted.
        """
        # The following line is crucial for the audit logging system to function.
        import inventory.signals