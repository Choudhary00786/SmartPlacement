from django.urls import path
from . import views

urlpatterns = [
    # Main Landing Page (Peheli baar aane walon ke liye)
    path('', views.landing_page, name='landing_page'),
    
    # Dashboard & Registration Routes
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/company/', views.company_register, name='company_register'),
    path('profile/', views.my_profile, name='my_profile'),
    path('applications/', views.my_applications, name='my_applications'),
    path('assessments/', views.assessments, name='assessments'),
    path('notifications/', views.notifications, name='notifications'),
    path('apply/<int:drive_id>/', views.apply_job, name='apply_job'),
]