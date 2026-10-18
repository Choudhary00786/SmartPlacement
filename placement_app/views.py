from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import JobDrive, Application, Student

@login_required(login_url='/admin/login/') # Abhi testing ke liye admin login use karenge
def student_dashboard(request):
    # Sirf active job drives fetch karein (DBMS SELECT Query)
    active_drives = JobDrive.objects.filter(is_active=True).order_by('deadline')
    
    # User se linked student profile fetch karein
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None

    context = {
        'drives': active_drives,
        'student': student
    }
    return render(request, 'student_dashboard.html', context)

@login_required(login_url='/admin/login/')
def apply_job(request, drive_id):
    job = get_object_or_404(JobDrive, id=drive_id)
    student = request.user.student

    # Rule 1: Check if already placed
    if student.is_placed:
        messages.error(request, 'Aap already placed hain. System aage apply karne ki permission nahi deta.')
        return redirect('student_dashboard')

    # Rule 2: CGPA Eligibility Check
    if student.cgpa < job.min_cgpa:
        messages.error(request, f'Is job ke liye minimum {job.min_cgpa} CGPA chahiye. Aapka CGPA {student.cgpa} hai.')
        return redirect('student_dashboard')

    # Rule 3: Duplicate Application Check
    if Application.objects.filter(student=student, job_drive=job).exists():
        messages.warning(request, 'Aapne is drive ke liye pehle hi apply kar diya hai!')
        return redirect('student_dashboard')

    # Agar saari conditions pass ho jayein, toh DBMS mein Application Table me record insert karein
    Application.objects.create(student=student, job_drive=job, status='Applied')
    messages.success(request, f'Aapne successfully {job.company.name} ke liye apply kar diya hai!')
    
    return redirect('student_dashboard')