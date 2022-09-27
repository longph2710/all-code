from django.urls import path
from . import views

urlpatterns = [
    path('jobs', views.add_backup_job),
    path('jobs/reconsile', views.call_reconcile),
    path('jobs/delete-all', views.delete_all_jobs),
    path('lock/', views.check_lock)
]