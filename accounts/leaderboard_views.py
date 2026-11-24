
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count

from .models import (
    StudentProfile,
    RecruiterProfile,
    ChallengeSubmission,
    ProjectEvidence
)


# STUDENT PERFORMANCE LEADERBOARD
@login_required
def student_leaderboard(request):

    # Allow only authenticated recruiters
    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    # Get students who have enabled public portfolios
    public_students = StudentProfile.objects.filter(
        is_public=True
    ).select_related('user')

    leaderboard = []

    # Calculate each student's verified performance
    for student in public_students:

        # Get verified challenge submissions with scores
        verified_challenges = ChallengeSubmission.objects.filter(
            student=student,
            status='VERIFIED',
            score__isnull=False
        )

        # Calculate average challenge score
        average_score = verified_challenges.aggregate(
            average=Avg('score')
        )['average']

        # Count verified projects
        verified_projects = ProjectEvidence.objects.filter(
            student=student,
            status='VERIFIED'
        ).count()

        # Include students with at least one verified score
        if average_score is not None:

            leaderboard.append({
                'student': student,
                'average_score': round(average_score, 2),
                'verified_challenges': verified_challenges.count(),
                'verified_projects': verified_projects
            })

    # Sort by average score, then verified project count
    leaderboard.sort(
        key=lambda item: (
            item['average_score'],
            item['verified_projects']
        ),
        reverse=True
    )

    # Assign ranking positions
    for position, item in enumerate(leaderboard, start=1):
        item['rank'] = position

    return render(
        request,
        'accounts/student_leaderboard.html',
        {
            'recruiter': recruiter,
            'leaderboard': leaderboard,
            'total_ranked_students': len(leaderboard)
        }
    )
