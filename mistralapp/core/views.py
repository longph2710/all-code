from django.shortcuts import render
from datetime import datetime

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *
from .scheduler import process_cron_triggers
from .lock import lock
# Create your views here.

class JobLCAPIView(ListCreateAPIView):
    queryset = CronJob.objects.filter()
    serializer_class = JobSerializer

    def post(self, request, *args, **kwargs):
        if not lock._held:
            print ('[%s] cant add job! lock is not held!' % datetime.now())
            return Response(status=status.HTTP_200_OK)
        return super().post(request, *args, **kwargs)

class JobRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = CronJob.objects.filter()
    serializer_class = JobSerializer
    lookup_field = 'instance'

@api_view(['GET'])
def process_backup(request):
    process_cron_triggers()
    return Response()