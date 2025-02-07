from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organization'

    def ready(self):
        import apps.organization.signals