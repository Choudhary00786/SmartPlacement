from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('apply/<int:drive_id>/', views.apply_job, name='apply_job'),
]