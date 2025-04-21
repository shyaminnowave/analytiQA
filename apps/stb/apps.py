from django.apps import AppConfig


class StbsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.stb'

    # def ready(self) -> None:
    #     import apps.stb.signals