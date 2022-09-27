from django.db import models

from datetime import datetime, tzinfo
from time import sleep
import uuid

from croniter import croniter
from dateutil import tz
# Create your models here.

class CronJob(models.Model):

    job_id = models.CharField(
        default='random-id-generate',
        max_length=255,
        unique=True
    )

    instance = models.CharField(null=True, max_length=100)

    zone = models.CharField(default='UTC', max_length=20)

    cron_time = models.CharField(
        null=False,
        max_length=50,
        help_text='UNIX cron format: minute hour day_of_month month day_of_week'
    )

    next_execution_time = models.DateTimeField(
        null=True
    )

    ENABLED='ENABLED'
    DISABLED='DISABLED'
    STATUS_CHOICES = [
        (ENABLED, 'ENABLED'),
        (DISABLED, 'DISABLED')
    ]
    
    status = models.CharField(
        default=ENABLED,
        choices=STATUS_CHOICES,
        max_length=10
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cron_time = self.cron_time

    def get_next_execution_time(self, auto_save=True):
        tzone = tz.gettz(self.zone)
        base = datetime.now(tzone)
        iter = croniter(self.cron_time, base)
        self.next_execution_time = iter.get_next(datetime)
        if auto_save:
            super().save(update_fields=['next_execution_time'])
        return self.next_execution_time

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None): 

        if self.job_id is None:
            self.job_id = str(uuid.uuid4())
        
        if self.next_execution_time is None or self.__cron_time != self.cron_time:     
            print ('update execution time')       
            self.get_next_execution_time(auto_save=False)
        
        return super().save(force_insert, force_update, using, update_fields)

    def execute(self):
        self.get_next_execution_time()
        sleep(10)
        print('job %s executed! next execution time at: %s' % (self.job_id, self.next_execution_time))
        
class JobExecution(models.Model):

    job = models.ForeignKey(CronJob, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    stop_time = models.DateTimeField(null=True)

    status = models.CharField(default='SUCCESS', max_length=10)

    def set_stop_status(self, stop_time=None, status='SUCCESS'):
        if stop_time is None:
            self.stop_time = datetime.now(tz=tz.gettz('UTC'))
        else: 
            self.stop_time=stop_time
        self.status = status
        self.save()
