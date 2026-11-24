
from django.contrib import admin

from .models import (
    StudentProfile,
    RecruiterProfile,
    SkillChallenge,
    ChallengeSubmission,
    ProjectEvidence
)


# STUDENT PROFILE ADMIN
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'college_name',
        'department',
        'graduation_year',
        'is_public'
    )

    search_fields = (
        'full_name',
        'college_name',
        'user__username'
    )

    list_filter = (
        'department',
        'graduation_year',
        'is_public'
    )


# RECRUITER PROFILE ADMIN
@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'company_name',
        'designation',
        'user'
    )

    search_fields = (
        'full_name',
        'company_name',
        'designation',
        'user__username'
    )


# SKILL CHALLENGE ADMIN
@admin.register(SkillChallenge)
class SkillChallengeAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'category',
        'difficulty',
        'is_active',
        'created_at'
    )

    search_fields = (
        'title',
        'description'
    )

    list_filter = (
        'category',
        'difficulty',
        'is_active'
    )


# CHALLENGE SUBMISSION ADMIN
@admin.register(ChallengeSubmission)
class ChallengeSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'challenge',
        'status',
        'score',
        'submitted_at'
    )

    search_fields = (
        'student__full_name',
        'challenge__title'
    )

    list_filter = (
        'status',
        'submitted_at'
    )

    list_editable = (
        'status',
        'score'
    )

    readonly_fields = (
        'submitted_at',
    )

    fieldsets = (
        ('Submission Information', {
            'fields': (
                'student',
                'challenge',
                'answer',
                'submitted_at'
            )
        }),

        ('Mentor Evaluation', {
            'fields': (
                'status',
                'score',
                'feedback'
            )
        }),
    )


# PROJECT EVIDENCE ADMIN
@admin.register(ProjectEvidence)
class ProjectEvidenceAdmin(admin.ModelAdmin):

    list_display = (
        'project_title',
        'student',
        'status',
        'submitted_at'
    )

    search_fields = (
        'project_title',
        'student__full_name'
    )

    list_filter = (
        'status',
        'submitted_at'
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'submitted_at',
    )

    fieldsets = (
        ('Project Information', {
            'fields': (
                'student',
                'project_title',
                'description',
                'github_link',
                'project_report',
                'project_screenshot',
                'submitted_at'
            )
        }),

        ('Mentor Verification', {
            'fields': (
                'status',
                'mentor_feedback'
            )
        }),
    )
