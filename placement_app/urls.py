from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/company/', views.company_register, name='company_register'),
    path('profile/', views.my_profile, name='my_profile'),
    path('applications/', views.my_applications, name='my_applications'),
    path('assessments/', views.assessments, name='assessments'),
    path('notifications/', views.notifications, name='notifications'),
    path('apply/<int:drive_id>/', views.apply_job, name='apply_job'),
]