# dbasscheduler/__init__.py

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .ce import app as celery_app, lock
from celery.signals import worker_process_init

__all__ = ['celery_app']

@worker_process_init.connect()
def worker_init_handler(*args, **kwargs):
    if not lock.locked():
        lock.acquire()
        print('acquired!')