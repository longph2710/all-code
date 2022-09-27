from math import floor
import os
from datetime import datetime
from dateutil import tz
import requests
import json

from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from celery import shared_task

from .models import CronJob, JobExecution
from .serializers import JobSerializer

scheduler = BackgroundScheduler()

@shared_task
def process_cron_triggers():
    print('processing ...')
    now = datetime.now(tz=tz.gettz('UTC'))
    # print(now)
    jobs = CronJob.objects.filter(next_execution_time__lte=now)
    # print(jobs)
    for job in jobs:
        start_time = datetime.now(tz=tz.gettz('UTC'))
        execution = JobExecution(job=job, start_time=start_time, status='RUNNING')
        execution.save()
        job.execute()
        execution.set_stop_status()

    return

@shared_task
def perform_reconsile():
    print('reconsiling ...')
    base_url = settings.DBAAS_BASE_URL
    user = os.environ.get('AUTH_USER')
    password = os.environ.get('AUTH_PASSWORD')
    
    # update job
    get_url = base_url + 'api/jobs/'
    job_list = json.loads(requests.get(url=get_url, auth=(user, password)).text)
    # print(type(job_list))
    for job in job_list:
        # print(job)
        # job_id, status, unix_cron_time, instance
        try:
            obj = CronJob.objects.get(job_id=job['job_id'])
            # update job
            update_fields = []
            is_changed = False

            if job['cron_time'] != obj.cron_time:
                obj.cron_time = job['cron_time']
                update_fields.insert('cron_time')
                is_changed = True
            if job['status'] != obj.status:
                obj.status = job['status']
                obj.insert('status')
                is_changed = True
            if is_changed:
                obj.save(update_fields=update_fields)
                print('updated!' + obj['job_id'])
        except CronJob.DoesNotExist:
            obj = None
            # create job
            new_obj = CronJob(
                job_id=job['job_id'], 
                instance=job['instance'],
                cron_time=job['cron_time'],
                status=job['status']
            )
            new_obj.save()
            print('created!' + new_obj.job_id)
    # delete job
    for job in CronJob.objects.all():
        if not bi_search(job_list, job.job_id):
            print('deleted!' + job.job_id)
            job.delete()
            
    return

def is_running():
    return scheduler.running

def call_cron_triggers():
    print('[%s] calling backup job!' % datetime.now())
    process_cron_triggers.delay()
    
def call_reconsile_job():
    print('[%s] calling reconsile job!' % datetime.now())
    perform_reconsile.delay()

def start():
    scheduler.add_job(
        id=os.environ.get('PROCESS_CRON_TRIGGERS_JOB_NAME'),
        func=call_cron_triggers,
        trigger='interval',
        minutes=1,
        replace_existing=True
    )
    scheduler.add_job(
        id=os.environ.get('PERFORM_RECONSILE_TRGGER_NAME'),
        func=call_reconsile_job,
        trigger='interval',
        minutes=2,
        replace_existing=True
    )
    scheduler.start()
    print('[%s] scheduler started!' % datetime.now())
    
def shutdown():
    scheduler.shutdown()
    print('[%s] scheduler shuted down!' % datetime.now())


def bi_search(job_list, job_id):
    low = 0
    hight = len(job_list)-1

    while low <= hight:
        mid = floor((low+hight)/2)
        if job_list[low]['job_id'] == job_id or job_list[hight]['job_id'] == job_id or job_list[mid]['job_id'] == job_id:
            return True
        if job_id < job_list[mid]['job_id']:
            hight = mid-1
        else:
            low = mid+1
    return False
