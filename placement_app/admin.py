from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Company, Student, JobDrive, Application, Interview

# Admin dashboard interface customize karne ke liye classes
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry_type', 'hr_email')
    search_fields = ('name', 'hr_email')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('usn', 'user', 'branch', 'cgpa', 'is_placed')
    list_filter = ('branch', 'is_placed')
    search_fields = ('usn', 'user__first_name')

@admin.register(JobDrive)
class JobDriveAdmin(admin.ModelAdmin):
    list_display = ('company', 'job_role', 'package_lpa', 'deadline', 'is_active')
    list_filter = ('is_active', 'company')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job_drive', 'status', 'applied_on')
    list_filter = ('status', 'job_drive')

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'interview_type', 'scheduled_datetime')