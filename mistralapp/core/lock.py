from django.conf import settings
from datetime import datetime
from time import sleep
import os

from redis import Redis
from redis_lock import Lock

from . import scheduler
# from common import globals
from common.lock import lock_app

conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
lock = Lock(conn, name=settings.CHECK_REDIS_LOCK_JOB_NAME,expire=60)

def check_redis_lock():
    sleep(5)
    if lock_app.locked():
        print('WORKER STARTED!')
        return

    while True:
        if lock._held:
            lock.extend(60)
            print('[%s] lock extend!' % datetime.now())
        elif lock.acquire(timeout=10):
            print('[%s] got lock!' % datetime.now())
            scheduler.start()
        else:
            if scheduler.is_running():
                scheduler.shutdown()
            print('[%s] someone has lock!' % datetime.now())
        sleep(30)