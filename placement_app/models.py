from django.db import models
from django.contrib.auth.models import User

# 1. Company Table
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    industry_type = models.CharField(max_length=100)
    hr_email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

# 2. Student Table (Linked with Django's login system)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usn = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=50)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    profile_completion = models.IntegerField(default=0) # UI mein 75% dikhane ke liye
    is_placed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} ({self.usn})"

# 3. Job Drive Table (1:N Relation with Company)
class JobDrive(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    package_lpa = models.DecimalField(max_digits=5, decimal_places=2)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    location = models.CharField(max_length=100, default='Hyderabad')
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.name} - {self.job_role}"

# 4. Application Table (M:N Relation Break down)
class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Assessment', 'Assessment'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected')
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job_drive = models.ForeignKey(JobDrive, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_on = models.DateTimeField(auto_now_add=True)

    # DBMS Constraint: Ek student ek company ki ek drive mein dobara apply na kar sake
    class Meta:
        unique_together = ('student', 'job_drive')

    def __str__(self):
        return f"{self.student.usn} -> {self.job_drive.job_role}"

# 5. Interview Tracking Table (1:N Relation with Application)
class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    interview_type = models.CharField(max_length=50) # e.g., Aptitude, Technical, HR
    scheduled_datetime = models.DateTimeField()
    meeting_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.application.student.usn} - {self.interview_type}"