from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection # <--- Ye naya import hai RAW SQL chalane ke liye
from .models import JobDrive, Application, Student

def landing_page(request):
    # Agar user pehle se login hai toh seedha dashboard bhejein
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    # First-time / non-logged-in user ke liye Landing Page
    return render(request, 'landing.html')

@login_required(login_url='/admin/login/')
def student_dashboard(request):
    # 1. RAW SQL SELECT & INNER JOIN (Professor ko dikhane ke liye)
    # Ye query JobDrive aur Company table ko SQL level par join karti hai
    sql_query = """
        SELECT d.id, c.name AS company_name, c.industry_type, 
               d.job_role, d.package_lpa, d.deadline, d.min_cgpa
        FROM placement_app_jobdrive d
        INNER JOIN placement_app_company c ON d.company_id = c.id
        WHERE d.is_active = 1
        ORDER BY d.deadline ASC;
    """
    
    # Query ko execute karna
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]
        drives = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # User se linked student profile fetch karein
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None

    context = {
        'drives': drives,
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

    with connection.cursor() as cursor:
        # 3. RAW SQL SELECT (Duplicate Application Check karne ke liye)
        check_query = "SELECT id FROM placement_app_application WHERE student_id = %s AND job_drive_id = %s"
        cursor.execute(check_query, [student.id, job.id])
        already_applied = cursor.fetchone()
        
        if already_applied:
            messages.warning(request, 'Aapne is drive ke liye pehle hi apply kar diya hai!')
            return redirect('student_dashboard')
            
        # 4. RAW SQL INSERT INTO (Nayi application database me save karne ke liye)
        insert_query = """
            INSERT INTO placement_app_application (status, applied_on, job_drive_id, student_id) 
            VALUES ('Applied', CURRENT_TIMESTAMP, %s, %s);
        """
        cursor.execute(insert_query, [job.id, student.id])

    messages.success(request, f'Aapne successfully {job.company.name} ke liye apply kar diya hai!')
    return redirect('student_dashboard')

from django.contrib.auth.models import User

def student_register(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        f_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        course = request.POST.get('course')    # e.g., B.Tech / M.Tech / MCA
        branch = request.POST.get('branch')    # e.g., CSE / ECE
        cgpa = request.POST.get('cgpa')

        # Branch text formatting (e.g. "B.Tech - CSE") for database storage
        full_branch_info = f"{course} - {branch}"

        try:
            # 1. User Creation
            user = User.objects.create_user(username=u_name, email=email, password=password, first_name=f_name)
            
            # 2. RAW SQL INSERT Query
            with connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO placement_app_student (branch, cgpa, is_placed, user_id) 
                    VALUES (%s, %s, 0, %s);
                """
                cursor.execute(insert_query, [full_branch_info, cgpa, user.id])
                
            messages.success(request, 'Registration successful! Ab aap login kar sakte hain.')
            return redirect('/admin/login/')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            
    return render(request, 'student_register.html')

def company_register(request):
    if request.method == 'POST':
        # Form se data nikalna
        name = request.POST.get('name')
        industry = request.POST.get('industry_type')
        email = request.POST.get('email')
        website = request.POST.get('website')

        try:
            # RAW SQL se Company table me data INSERT karein
            with connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO placement_app_company (name, industry_type, email, website) 
                    VALUES (%s, %s, %s, %s);
                """
                cursor.execute(insert_query, [name, industry, email, website])
                
            messages.success(request, 'Company Registration Successful!')
            return redirect('student_dashboard') # Ya admin panel bhej sakte hain
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            
    return render(request, 'company_register.html')

from django.db import connection

@login_required(login_url='/admin/login/')
def my_profile(request):
    student_id = request.user.student.id
    # RAW SQL Query for Student Profile + User Auth Data
    with connection.cursor() as cursor:
        sql = """
            SELECT s.id, u.first_name, u.email, u.username, s.branch, s.cgpa, s.is_placed
            FROM placement_app_student s
            INNER JOIN auth_user u ON s.user_id = u.id
            WHERE s.id = %s;
        """
        cursor.execute(sql, [student_id])
        row = cursor.fetchone()
        
    profile_data = {
        'id': row[0], 'name': row[1], 'email': row[2], 
        'username': row[3], 'branch': row[4], 'cgpa': row[5], 'is_placed': row[6]
    } if row else None

    return render(request, 'my_profile.html', {'profile': profile_data})


@login_required(login_url='/admin/login/')
def my_applications(request):
    student_id = request.user.student.id
    # RAW SQL Multi-Table INNER JOIN (Application + JobDrive + Company)
    with connection.cursor() as cursor:
        sql = """
            SELECT a.id, c.name AS company_name, d.job_role, d.package_lpa, a.status, a.applied_on
            FROM placement_app_application a
            INNER JOIN placement_app_jobdrive d ON a.job_drive_id = d.id
            INNER JOIN placement_app_company c ON d.company_id = c.id
            WHERE a.student_id = %s
            ORDER BY a.applied_on DESC;
        """
        cursor.execute(sql, [student_id])
        columns = [col[0] for col in cursor.description]
        apps = [dict(zip(columns, r)) for r in cursor.fetchall()]

    return render(request, 'my_applications.html', {'applications': apps})


@login_required(login_url='/admin/login/')
def assessments(request):
    return render(request, 'assessments.html')


@login_required(login_url='/admin/login/')
def notifications(request):
    return render(request, 'notifications.html')