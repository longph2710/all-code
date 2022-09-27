
from django.apps import AppConfig
from datetime import datetime
from django.conf import settings

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # from multiprocessing import Process
        from threading import Thread
        from .updater import check_redis_lock, scheduler
        if settings.SCHEDULER_AUTOSTART:
            daemon = Thread(daemon=True, target=check_redis_lock, name='thread-check-lock')
            daemon.start()
