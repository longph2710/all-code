from dataclasses import field
from rest_framework.serializers import ModelSerializer
from django_apscheduler.models import DjangoJob

class JobSerializer(ModelSerializer):
    class Meta:
        model = DjangoJob
        fields = '__all__'