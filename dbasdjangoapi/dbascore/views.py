from copy import copy
from django.shortcuts import render
from django.conf import settings
import requests
import json

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *
from .models import DatabaseInstance, BackupPolicy

# Create your views here.
class DBListCreateAPIView(generics.ListCreateAPIView):
    queryset = DatabaseInstance.objects.filter()
    serializer_class = DatabaseSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class DBRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DatabaseInstance.objects.filter()
    serializer_class = DatabaseSerializer

    lookup_field = 'name'

    def get_queryset(self):
        queryset = DatabaseInstance.objects.filter()
        return queryset

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        policiy = BackupPolicy.objects.get(instance=instance)
        serializer = PolicySerializer(policiy)
        serializer.delete()
        return super().delete(request, *args, **kwargs)

class PolicyListCreateAPIView(generics.ListCreateAPIView):
    queryset = BackupPolicy.objects.filter()
    serializer_class = PolicySerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class PolicyRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BackupPolicy.objects.filter()
    serializer_class = PolicySerializer

    lookup_field = 'job_id'

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PolicySerializer(instance)
        serializer.delete()
        return super().delete(request, *args, **kwargs)

@api_view(['GET'])
def get_list_job(request):
    response = []
    jobs = BackupPolicy.objects.order_by('job_id')
    for job in jobs:
        response.insert(job.id, job.to_json_data())
    return Response(response)