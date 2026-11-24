
from django.db.models import Avg, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .forms import StudentRegistrationForm, ProjectEvidenceForm

from .models import (
    StudentProfile,
    RecruiterProfile,
    SkillChallenge,
    ChallengeSubmission,
    ProjectEvidence
)


# STUDENT REGISTRATION
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()

                StudentProfile.objects.create(
                    user=user,
                    full_name=form.cleaned_data['full_name'],
                    college_name=form.cleaned_data['college_name'],
                    department=form.cleaned_data['department'],
                    graduation_year=form.cleaned_data['graduation_year']
                )

            return render(
                request,
                'accounts/register.html',
                {
                    'form': StudentRegistrationForm(),
                    'success': 'Student account created successfully!'
                }
            )

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


# STUDENT LOGIN
def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            if StudentProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('student_dashboard')

        return render(
            request,
            'accounts/login.html',
            {'error': 'Invalid student username or password.'}
        )

    return render(request, 'accounts/login.html')


# STUDENT DASHBOARD
@login_required
def student_dashboard(request):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    total_challenges = SkillChallenge.objects.filter(
        is_active=True
    ).count()

    total_submissions = ChallengeSubmission.objects.filter(
        student=profile
    ).count()

    return render(
        request,
        'accounts/dashboard.html',
        {
            'profile': profile,
            'total_challenges': total_challenges,
            'total_submissions': total_submissions
        }
    )


# DISPLAY AVAILABLE CHALLENGES
@login_required
def challenge_list(request):
    challenges = SkillChallenge.objects.filter(
        is_active=True
    ).order_by('-created_at')

    return render(
        request,
        'accounts/challenge_list.html',
        {'challenges': challenges}
    )


# DISPLAY CHALLENGE DETAILS
@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(
        SkillChallenge,
        id=challenge_id,
        is_active=True
    )

    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    previous_submissions = ChallengeSubmission.objects.filter(
        student=profile,
        challenge=challenge
    ).order_by('-submitted_at')

    return render(
        request,
        'accounts/challenge_detail.html',
        {
            'challenge': challenge,
            'previous_submissions': previous_submissions,
            'submitted': request.GET.get('submitted') == '1'
        }
    )


# SUBMIT CHALLENGE ANSWER
@login_required
def submit_challenge(request, challenge_id):
    if request.method != 'POST':
        return redirect(
            'challenge_detail',
            challenge_id=challenge_id
        )

    challenge = get_object_or_404(
        SkillChallenge,
        id=challenge_id,
        is_active=True
    )

    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    answer = request.POST.get('answer', '').strip()

    if not answer:
        previous_submissions = ChallengeSubmission.objects.filter(
            student=profile,
            challenge=challenge
        ).order_by('-submitted_at')

        return render(
            request,
            'accounts/challenge_detail.html',
            {
                'challenge': challenge,
                'previous_submissions': previous_submissions,
                'error': 'Please enter your answer before submitting.'
            }
        )

    ChallengeSubmission.objects.create(
        student=profile,
        challenge=challenge,
        answer=answer
    )

    detail_url = reverse(
        'challenge_detail',
        args=[challenge.id]
    )

    return redirect(f'{detail_url}?submitted=1')


# PROJECT EVIDENCE UPLOAD
@login_required
def upload_project(request):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    if request.method == 'POST':
        form = ProjectEvidenceForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            project = form.save(commit=False)
            project.student = profile
            project.save()

            return redirect('my_projects')

    else:
        form = ProjectEvidenceForm()

    return render(
        request,
        'accounts/upload_project.html',
        {'form': form}
    )


# DISPLAY STUDENT PROJECTS
@login_required
def my_projects(request):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    projects = ProjectEvidence.objects.filter(
        student=profile
    ).order_by('-submitted_at')

    return render(
        request,
        'accounts/my_projects.html',
        {'projects': projects}
    )


# STUDENT LOGOUT
def student_logout(request):
    logout(request)
    return redirect('student_login')


# SKILL FINGERPRINT DASHBOARD
@login_required
def skill_fingerprint(request):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    skill_scores = (
        ChallengeSubmission.objects
        .filter(
            student=profile,
            score__isnull=False
        )
        .values('challenge__category')
        .annotate(average_score=Avg('score'))
        .order_by('challenge__category')
    )

    verified_projects = ProjectEvidence.objects.filter(
        student=profile,
        status='VERIFIED'
    ).count()

    total_projects = ProjectEvidence.objects.filter(
        student=profile
    ).count()

    total_submissions = ChallengeSubmission.objects.filter(
        student=profile
    ).count()

    return render(
        request,
        'accounts/skill_fingerprint.html',
        {
            'profile': profile,
            'skill_scores': skill_scores,
            'verified_projects': verified_projects,
            'total_projects': total_projects,
            'total_submissions': total_submissions
        }
    )


# SKILL GROWTH TIMELINE
@login_required
def skill_growth_timeline(request):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    submissions = (
        ChallengeSubmission.objects
        .filter(
            student=profile,
            score__isnull=False
        )
        .select_related('challenge')
        .order_by('submitted_at')
    )

    total_evaluated = submissions.count()

    first_score = None
    latest_score = None
    score_change = None

    if total_evaluated >= 1:
        first_score = submissions.first().score
        latest_score = submissions.last().score

    if total_evaluated >= 2:
        score_change = latest_score - first_score

    return render(
        request,
        'accounts/skill_growth_timeline.html',
        {
            'profile': profile,
            'submissions': submissions,
            'total_evaluated': total_evaluated,
            'first_score': first_score,
            'latest_score': latest_score,
            'score_change': score_change
        }
    )


# PUBLIC STUDENT PORTFOLIO
def public_student_portfolio(request, username):
    student_user = get_object_or_404(
        User,
        username=username
    )

    profile = get_object_or_404(
        StudentProfile,
        user=student_user
    )

    if not profile.is_public:
        return render(
            request,
            'accounts/portfolio_private.html',
            {'profile': profile},
            status=403
        )

    verified_projects = ProjectEvidence.objects.filter(
        student=profile,
        status='VERIFIED'
    ).order_by('-submitted_at')

    verified_challenges = (
        ChallengeSubmission.objects
        .filter(
            student=profile,
            status='VERIFIED',
            score__isnull=False
        )
        .select_related('challenge')
        .order_by('-submitted_at')
    )

    return render(
        request,
        'accounts/public_portfolio.html',
        {
            'profile': profile,
            'verified_projects': verified_projects,
            'verified_challenges': verified_challenges,
            'total_verified_projects': verified_projects.count(),
            'total_verified_challenges': verified_challenges.count()
        }
    )


# STUDENT PORTFOLIO PRIVACY SETTINGS
@login_required
@require_POST
def portfolio_settings(request):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    action = request.POST.get('action')

    if action == 'enable':
        profile.is_public = True
        profile.save(update_fields=['is_public'])

    elif action == 'disable':
        profile.is_public = False
        profile.save(update_fields=['is_public'])

    return redirect('student_dashboard')


# RECRUITER LOGIN
def recruiter_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            recruiter_exists = RecruiterProfile.objects.filter(
                user=user
            ).exists()

            if recruiter_exists:
                login(request, user)
                return redirect('recruiter_dashboard')

        return render(
            request,
            'accounts/recruiter_login.html',
            {
                'error': 'Invalid recruiter username or password.'
            }
        )

    return render(
        request,
        'accounts/recruiter_login.html'
    )


# RECRUITER DASHBOARD WITH SEARCH AND FILTER
@login_required
def recruiter_dashboard(request):
    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    public_students = StudentProfile.objects.filter(
        is_public=True
    ).select_related('user')

    search_query = request.GET.get('q', '').strip()
    selected_department = request.GET.get('department', '').strip()
    selected_year = request.GET.get('year', '').strip()
    selected_skill = request.GET.get('skill', '').strip()

    if search_query:
        public_students = public_students.filter(
            Q(full_name__icontains=search_query) |
            Q(college_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    valid_departments = [
        choice[0] for choice in StudentProfile.DEPARTMENT_CHOICES
    ]

    if selected_department in valid_departments:
        public_students = public_students.filter(
            department=selected_department
        )

    if selected_year.isdigit():
        public_students = public_students.filter(
            graduation_year=int(selected_year)
        )

    valid_skills = [
        choice[0] for choice in SkillChallenge.CATEGORY_CHOICES
    ]

    if selected_skill in valid_skills:
        public_students = public_students.filter(
            challenge_submissions__status='VERIFIED',
            challenge_submissions__challenge__category=selected_skill
        ).distinct()

    public_students = public_students.order_by('full_name')

    return render(
        request,
        'accounts/recruiter_dashboard.html',
        {
            'recruiter': recruiter,
            'public_students': public_students,
            'total_public_students': public_students.count(),
            'search_query': search_query,
            'selected_department': selected_department,
            'selected_year': selected_year,
            'selected_skill': selected_skill,
            'department_choices': StudentProfile.DEPARTMENT_CHOICES,
            'skill_choices': SkillChallenge.CATEGORY_CHOICES
        }
    )


# RECRUITER SKILL ASSESSMENT VIEW
@login_required
def recruiter_student_assessment(request, username):

    # Verify that the logged-in user is a recruiter
    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    # Recruiter can view only public student profiles
    student = get_object_or_404(
        StudentProfile.objects.select_related('user'),
        user__username=username,
        is_public=True
    )

    # Get verified challenge submissions with scores
    verified_challenges = (
        ChallengeSubmission.objects
        .filter(
            student=student,
            status='VERIFIED',
            score__isnull=False
        )
        .select_related('challenge')
        .order_by('-submitted_at')
    )

    # Calculate average score for each verified skill
    skill_scores = (
        verified_challenges
        .values('challenge__category')
        .annotate(average_score=Avg('score'))
        .order_by('challenge__category')
    )

    # Get mentor-verified projects
    verified_projects = ProjectEvidence.objects.filter(
        student=student,
        status='VERIFIED'
    ).order_by('-submitted_at')

    # Count verified challenges and projects
    total_verified_challenges = verified_challenges.count()
    total_verified_projects = verified_projects.count()

    return render(
        request,
        'accounts/recruiter_student_assessment.html',
        {
            'recruiter': recruiter,
            'student': student,
            'verified_challenges': verified_challenges,
            'skill_scores': skill_scores,
            'verified_projects': verified_projects,
            'total_verified_challenges': total_verified_challenges,
            'total_verified_projects': total_verified_projects
        }
    )


# RECRUITER STUDENT COMPARISON
@login_required
def recruiter_compare_students(request):

    # Check whether the logged-in user is a recruiter
    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    # Get all public student profiles
    public_students = StudentProfile.objects.filter(
        is_public=True
    ).select_related('user').order_by('full_name')

    # Get selected student usernames
    username_one = request.GET.get('student1', '').strip()
    username_two = request.GET.get('student2', '').strip()

    # Initialize variables before conditions
    student_one = None
    student_two = None

    student_one_challenges = 0
    student_two_challenges = 0

    student_one_projects = 0
    student_two_projects = 0

    comparison_rows = []
    error = None

    # Continue only when both students are selected
    if username_one and username_two:

        # Prevent comparing the same student
        if username_one == username_two:

            error = 'Please select two different students.'

        else:

            # Get first public student
            student_one = get_object_or_404(
                StudentProfile.objects.select_related('user'),
                user__username=username_one,
                is_public=True
            )

            # Get second public student
            student_two = get_object_or_404(
                StudentProfile.objects.select_related('user'),
                user__username=username_two,
                is_public=True
            )

            # First student's verified scored challenges
            first_verified = ChallengeSubmission.objects.filter(
                student=student_one,
                status='VERIFIED',
                score__isnull=False
            ).select_related('challenge')

            # Second student's verified scored challenges
            second_verified = ChallengeSubmission.objects.filter(
                student=student_two,
                status='VERIFIED',
                score__isnull=False
            ).select_related('challenge')

            # Calculate category-wise average for first student
            first_scores = first_verified.values(
                'challenge__category'
            ).annotate(
                average_score=Avg('score')
            )

            # Calculate category-wise average for second student
            second_scores = second_verified.values(
                'challenge__category'
            ).annotate(
                average_score=Avg('score')
            )

            # Convert results into dictionaries
            first_score_dict = {
                item['challenge__category']: item['average_score']
                for item in first_scores
            }

            second_score_dict = {
                item['challenge__category']: item['average_score']
                for item in second_scores
            }

            # Combine all available skill categories
            all_categories = sorted(
                set(first_score_dict.keys()) |
                set(second_score_dict.keys())
            )

            # Prepare comparison rows
            for category in all_categories:

                comparison_rows.append({
                    'category': category,
                    'score_one': first_score_dict.get(category),
                    'score_two': second_score_dict.get(category)
                })

            # Count verified scored challenges
            student_one_challenges = first_verified.count()
            student_two_challenges = second_verified.count()

            # Count verified projects
            student_one_projects = ProjectEvidence.objects.filter(
                student=student_one,
                status='VERIFIED'
            ).count()

            student_two_projects = ProjectEvidence.objects.filter(
                student=student_two,
                status='VERIFIED'
            ).count()

    return render(
        request,
        'accounts/recruiter_compare_students.html',
        {
            'recruiter': recruiter,
            'public_students': public_students,
            'student_one': student_one,
            'student_two': student_two,
            'comparison_rows': comparison_rows,
            'student_one_challenges': student_one_challenges,
            'student_two_challenges': student_two_challenges,
            'student_one_projects': student_one_projects,
            'student_two_projects': student_two_projects,
            'error': error
        }
    )


# RECRUITER LOGOUT
def recruiter_logout(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect('recruiter_login')
