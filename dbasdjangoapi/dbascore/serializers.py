import requests, json
from threading import Thread

from dataclasses import fields
from rest_framework import serializers
from .models import *
from .tasks import request_action

class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseInstance
        fields = ['name', 'desctiption']

    def delete(self):
        sending_data = json.dumps(self.data)
        for prefix in settings.SCHEDULER_URL:
            try:
                url = prefix + 'api/jobs'
                requests.delete(url=url, json=sending_data)
                print("deleted to: %s" % url)
            except Exception:
                print ('deleted to put: %s' % url)
        return True

class PolicySerializer(serializers.ModelSerializer):

    # instance_name = serializers.CharField(source='instance.name')

    class Meta:
        model = BackupPolicy
        fields = '__all__'
        # fields = ['job_name', 'status', 'job_state', 'instance_name']

    def create(self, validated_data):
        policy = super().create(validated_data)
        # print(type(validated_data))
        sending_data = policy.to_json_data()

        kwargs = {
            'method' : 'post',
            'json' : sending_data
        }

        post_thread = Thread(daemon=True, target=request_action, kwargs=kwargs)
        post_thread.start()
        return policy

    def update(self, instance, validated_data):
        policy = super().update(instance, validated_data)
        # print(self.data)
        sending_data = policy.to_json_data()

        kwargs = {
            'method' : 'put',
            'json' : sending_data
        }

        put_thread = Thread(daemon=True, target=request_action, kwargs=kwargs)
        put_thread.start()
        return policy

    def delete(self):
        sending_data = self.data

        kwargs = {
            'method' : 'delete',
            'json' : sending_data
        }

        delete_thread = Thread(daemon=True, target=request_action, kwargs=kwargs)
        delete_thread.start()
        return True