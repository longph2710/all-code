from django.shortcuts import render
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_apscheduler.models import DjangoJob

from .serializers import *
from .updater import scheduler, lock, perform_add_backup_job, perform_reconsile, perform_delete_job

# Create your views here.

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def add_backup_job(request):
    if not lock._held:
        return Response(status=status.HTTP_200_OK)

    if request.method == 'GET':
        jobs = DjangoJob.objects.filter()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    data = json.loads(request.data)
    print(data)
    if request.method == 'POST' or request.method == 'PUT':
        # perform add/update
        perform_add_backup_job(
            job_id=data['job_id'],
            job_state=data['job_state'],
            instance_id=data['instance']
        )
        print('created/updated!')
        return Response(status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        perform_delete_job(job_id=data['job_id'])
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # data = request.data
    # scheduler.add_backup_job(
    #     job_id=data.get('job_name'), 
    #     job_state=data.get('job_state'), 
    #     instance_id=data.get('instance')
    # )
    # print(data.get('job_state'))

@api_view(['GET'])
def call_reconcile(request):
    perform_reconsile()
    return Response({"running" : scheduler.running})

@api_view(['DELETE'])
def delete_all_jobs(request):
    scheduler.remove_all_jobs()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def check_lock(request):
    return Response({"locking" : lock._held})