
from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    DEPARTMENT_CHOICES = [
        ('BCA', 'BCA'),
        ('BSC', 'B.Sc'),
        ('BTECH', 'B.Tech'),
        ('BE', 'B.E'),
        ('MCA', 'MCA'),
        ('OTHER', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    full_name = models.CharField(max_length=100)
    college_name = models.CharField(max_length=150)

    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES
    )

    graduation_year = models.PositiveIntegerField()
    bio = models.TextField(blank=True)

    profile_photo = models.ImageField(
        upload_to='student_profiles/',
        blank=True,
        null=True
    )

    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


# RECRUITER PROFILE
class RecruiterProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )

    full_name = models.CharField(max_length=100)

    company_name = models.CharField(max_length=150)

    designation = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.company_name}"


# SKILL CHALLENGE
class SkillChallenge(models.Model):

    CATEGORY_CHOICES = [
        ('PYTHON', 'Python'),
        ('SQL', 'SQL'),
        ('HTML', 'HTML'),
        ('CSS', 'CSS'),
        ('JAVASCRIPT', 'JavaScript'),
    ]

    DIFFICULTY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    title = models.CharField(max_length=200)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES
    )

    description = models.TextField()
    instructions = models.TextField()
    starter_code = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# CHALLENGE SUBMISSION
class ChallengeSubmission(models.Model):

    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('VERIFIED', 'Verified'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='challenge_submissions'
    )

    challenge = models.ForeignKey(
        SkillChallenge,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    answer = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='SUBMITTED'
    )

    score = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.challenge.title}"


# PROJECT EVIDENCE
class ProjectEvidence(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='project_evidences'
    )

    project_title = models.CharField(max_length=200)

    description = models.TextField()

    github_link = models.URLField(blank=True)

    project_report = models.FileField(
        upload_to='project_reports/',
        blank=True,
        null=True
    )

    project_screenshot = models.ImageField(
        upload_to='project_screenshots/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    mentor_feedback = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_title
