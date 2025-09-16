from django.apps import AppConfig
import os
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        media_path = settings.MEDIA_ROOT
        if media_path and not os.path.exists(media_path):
            os.makedirs(media_path)
