from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from . import lock
        from threading import Thread

        daemon_thread = Thread(daemon=True, target=lock.check_redis_lock)
        daemon_thread.start()