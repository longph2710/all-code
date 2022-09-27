from django.conf import settings
from redis import Redis
from redis_lock import Lock

import os

conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
lock_app = Lock(conn, name=settings.APP_WORKER_LOCK_NAME, expire=15)