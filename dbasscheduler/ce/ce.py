import os
from django.conf import settings
from celery import Celery
from celery.bin.worker import worker
from redis import Redis
import redis_lock
from dotenv import load_dotenv
# set the default Django settings module for the 'celery' program.
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbasscheduler.settings')
# os.environ["SCHEDULER_AUTOSTART"] = False

broker_url = 'redis://%s:%s/0' % (os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))

app = Celery('ce', broker=broker_url)

conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
lock = redis_lock.Lock(conn, name=settings.CELERY_LOCK_NAME, expire=60)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
