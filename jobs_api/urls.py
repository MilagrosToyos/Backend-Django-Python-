from django.urls import path
from . import views

urlpatterns = [
    path('linkedin-jobs/', views.get_linkedin_jobs, name='get_linkedin_jobs'),
]