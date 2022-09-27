from dataclasses import fields
from rest_framework import serializers
from .models import *
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

class JobSerializer(serializers.ModelSerializer):
    # next_execution_time = serializers.SerializerMethodField()

    next_execution_time = serializers.ReadOnlyField()

    class Meta:
        model = CronJob
        fields = ['instance', 'job_id', 'zone', 'cron_time', 'next_execution_time', 'status']

    # @extend_schema_field(OpenApiTypes.DATETIME)
    # def get_next_execution_time(self, obj):
    #     return obj.to_local_time()