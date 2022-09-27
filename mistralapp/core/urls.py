from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.JobLCAPIView.as_view()),
    path('jobs/<str:instance>/', views.JobRUDAPIView.as_view()),
    path('process-backup/', views.process_backup),
]