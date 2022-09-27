from multiprocessing.resource_sharer import stop
from django.conf import settings
import requests, json

from time import sleep
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from redis_lock import Lock
from redis import Redis
from rest_framework import status
from celery import shared_task

from ce.ce import lock as celery_lock

import os

# init --------------------------------------------
conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
lock = Lock(conn, name='lock-app-01', expire=60)

scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
# job_reconsile_name = ''
# scheduler.add_jobstore(DjangoJobStore(), 'default')

# scheduler --------------------------------------------

def print_scheduler():
    print('[%s] scheduler !' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def start_scheduler():
    if scheduler.running:
        return
    print('[%s] scheduler started!' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # scheduler.add_job(id='job-start', func=print, args=('___job start___'), trigger='interval', seconds=5, replace_existing=True)
    reconsile_interval_time = json.loads(os.environ.get('RECONSILE_INTERVAL_TIME'))
    scheduler.add_job(
        id=os.environ.get('RECONSILE_JOB_NAME'), 
        # func=perform_reconsile.delay, 
        func=perform_reconsile,
        trigger='interval', 
        **reconsile_interval_time, 
        replace_existing=True
    )
    scheduler.start()

    # register_events(scheduler)
    # scheduler.remove_all_jobs()
    # print(scheduler.running)

# lock -------------------------------------------

def check_redis_lock():
    sleep(5)
    if celery_lock.locked():
        print('locked!')
        # try:
        #     scheduler.start()
        #     scheduler.pause()
        # except Exception as e:
        #     print('already stared!')
        return
    while True:
    
        if lock._held:
            lock.extend(60)
            print('[%s] extend !' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elif lock.acquire(timeout=10):
            print('[%s] got lock !' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            start_scheduler()
        else:
            print('[%s] someone has lock !' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if scheduler.running:
                scheduler.shutdown()

        sleep(30)

# scheduler functions
@shared_task
def perform_add_backup_job(scheduler=scheduler, job_id=None, job_state=None, instance_id=None):
    job = scheduler.add_job(
        id=job_id,
        **job_state,
        func=call_backup_job.delay,
        # func=call_backup_job,
        kwargs={"id":instance_id},
        replace_existing=True
    )
    # print(job_state)
    return job

@shared_task
def call_backup_job(id):
    # if not lock._held:
    #     print('[%s] cant perform this backup: %s' % (datetime.now(), id))
    #     return
    print('[%s] call backup database: %s' % (datetime.now(), id))

@shared_task
def perform_reconsile(scheduler=scheduler):
    # print (scheduler.running)
    url = settings.DBAAS_API_URL + 'api/policies'
    prefix = url + '/'
    data_text = requests.get(url=url, auth=settings.AUTHENTICATION).text
    polices = json.loads(data_text)

    for policy in polices:
        job = scheduler.get_job(job_id=policy['job_id'])
        if job is not None:
            if policy['status'] != 'DISABLED':
                job.reschedule(**policy['job_state'])
            else:
                scheduler.remove_job(job_id=job.id)
            print('[%s] updated job: %s' % (datetime.now(), job.id))
        else:
            job = perform_add_backup_job(job_id=policy['job_id'], job_state=policy['job_state'], instance_id=policy['instance'])
            print('[%s] added job: %s' % (datetime.now(), job.id))

    for job in scheduler.get_jobs():
        if job.id == os.environ.get('RECONSILE_JOB_NAME'):
            return
        url_retrive = prefix + job.id
        response = requests.get(url=url_retrive, auth=settings.AUTHENTICATION)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            scheduler.remove_job(job_id=job.id)
            print('[%s] deleted job: %s' % (datetime.now(), job.id))

@shared_task
def perform_delete_job(job_id):
    try:
        scheduler.remove_job(job_id=job_id)
        print('[%s] deleted job: %s' % (datetime.now(), job_id))
    except JobLookupError as e:
        print('[%s] job doesnt exist: %s' % (datetime.now(), job_id))
            