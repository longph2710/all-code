import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mistralapp.settings')

broker_url = 'redis://%s:%s/0' % (os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))
app = Celery('ce', broker=broker_url)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
