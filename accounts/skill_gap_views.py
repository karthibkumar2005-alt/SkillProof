
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

from .models import (
    StudentProfile,
    ChallengeSubmission,
    SkillChallenge
)


@login_required
def student_skill_gap_analysis(request):

    # Get the logged-in student's profile
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    # Get all available skill categories
    skill_categories = SkillChallenge.CATEGORY_CHOICES

    skill_analysis = []

    # Analyse each skill separately
    for category_code, category_name in skill_categories:

        verified_submissions = ChallengeSubmission.objects.filter(
            student=profile,
            challenge__category=category_code,
            status='VERIFIED',
            score__isnull=False
        )

        # Calculate average score
        average_score = verified_submissions.aggregate(
            average=Avg('score')
        )['average']

        # Identify skill level
        if average_score is None:

            status = 'Not Assessed'
            recommendation = (
                'Complete a challenge to assess this skill.'
            )

        elif average_score >= 70:

            status = 'Strong'
            recommendation = (
                'Keep practising to maintain your performance.'
            )

        elif average_score >= 40:

            status = 'Developing'
            recommendation = (
                'Practise more challenges to improve this skill.'
            )

        else:

            status = 'Needs Improvement'
            recommendation = (
                'Focus on beginner-level challenges in this skill.'
            )

        # Find active challenges for this category
        recommended_challenges = SkillChallenge.objects.filter(
            category=category_code,
            is_active=True
        ).order_by('difficulty')[:3]

        skill_analysis.append({
            'skill_name': category_name,
            'average_score': (
                round(average_score, 2)
                if average_score is not None
                else None
            ),
            'status': status,
            'recommendation': recommendation,
            'verified_count': verified_submissions.count(),
            'recommended_challenges': recommended_challenges
        })

    # Calculate overall skill statistics
    total_skills = len(skill_analysis)

    strong_count = sum(
        1 for skill in skill_analysis
        if skill['status'] == 'Strong'
    )

    developing_count = sum(
        1 for skill in skill_analysis
        if skill['status'] == 'Developing'
    )

    improvement_count = sum(
        1 for skill in skill_analysis
        if skill['status'] == 'Needs Improvement'
    )

    not_assessed_count = sum(
        1 for skill in skill_analysis
        if skill['status'] == 'Not Assessed'
    )

    # Send all information to HTML page
    context = {
        'profile': profile,
        'skill_analysis': skill_analysis,

        'total_skills': total_skills,
        'strong_count': strong_count,
        'developing_count': developing_count,
        'improvement_count': improvement_count,
        'not_assessed_count': not_assessed_count,
    }

    return render(
        request,
        'accounts/skill_gap_analysis.html',
        context
    )
