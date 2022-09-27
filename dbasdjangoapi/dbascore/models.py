import json
from django.db import models
from django.conf import settings
import requests

# Create your models here.

class DatabaseInstance(models.Model):
    name = models.CharField(max_length=50, null=False)
    desctiption = models.TextField()
    is_deleted = models.BooleanField(default=False)
    
class BackupPolicy(models.Model):

    job_id = models.CharField(max_length=50, unique=True)

    instance = models.OneToOneField(DatabaseInstance, on_delete=models.CASCADE)

    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'
    STATUS_CHOICES = [
        (ENABLED, 'ENABLED'),
        (DISABLED, 'DISABLED')
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ENABLED
    )

    job_state = models.JSONField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        __state = {
            'minute' : '00',
            'hour' : '08', 
            'day_of_month' : '*',
            'month' : '*',
            'day_of_week' : '*'
        }
        if self.job_state is None:
            self.job_state = __state

    def to_json_data(self):
        minute = '*' if 'minute' not in self.job_state else self.job_state['minute']
        hour = '*' if 'hour' not in self.job_state else self.job_state['hour']
        day_of_month = '*' if 'day_of_month' not in self.job_state else self.job_state['day_of_month']
        month = '*' if 'month' not in self.job_state else self.job_state['month']
        day_of_week = '*' if 'day_of_week' not in self.job_state else self.job_state['day_of_week']
        
        data = {
            'instance' : self.instance.name,
            'job_id' : self.job_id,
            'zone' : 'Asia/Ho_Chi_Minh',
            'cron_time' : '%s %s %s %s %s' % (minute, hour, day_of_month, month, day_of_week),
            'status' : self.status
        }

        # print(data)

        return data

# class BackgroundRequest():

#     def __init__(self, 
#         user=settings.AUTHENTICATION_USER, 
#         password=settings.AUTHENTICATION_PASSWORD, 
#         token=None):
#         if token is None:
#             self.auth = (user, password)
    
#     def get(self, url, data=None, json=None):
#         requests.get(url, data=data, json=json, auth=self.auth)

#     def post(self, url, data=None, json=None):
#         requests.post(url, data=data, json=json, auth=self.auth)

#     def put(self, url, data=None, json=None):
#         requests.put(url, data=data, json=json, auth=self.auth)

#     def delete(self, url, data=None, json=None):
#         requests.delete(url, data=data, json=json, auth=self.auth)

#     def run_multiple_requests(self, method, list_url, kwargs):
#         request_method = getattr(self, method)
#         for url in list_url:
#             request_method(url, ** kwargs, auth=self.auth)