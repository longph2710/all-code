# dbasscheduler/__init__.py

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .ce import app as celery_app
from common.lock import lock_app
from celery.signals import worker_process_init
from common import globals

__all__ = ['celery_app']

@worker_process_init.connect()
def worker_init_handler(*args, **kwargs):
    if not lock_app.locked():
        lock_app.acquire()