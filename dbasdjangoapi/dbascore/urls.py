from django.urls import path

from . import views

urlpatterns = [
    path('databases', views.DBListCreateAPIView.as_view(), name='database-info'),
    path('databases/<str:name>', views.DBRetrieveUpdateDestroyAPIView.as_view(), name='database-action'),
    path('policies', views.PolicyListCreateAPIView.as_view(), name='policy-info'),
    path('policies/<str:job_id>', views.PolicyRetrieveUpdateAPIView.as_view(), name='policy-action'),
    path('jobs/', views.get_list_job)
]