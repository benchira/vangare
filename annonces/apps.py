from django.apps import AppConfig


class AnnoncesConfig(AppConfig):
    name = 'annonces'

    def ready(self):
        from . import signals
