
from django.urls import path
from . import views
from . import leaderboard_views
from . import skill_gap_views

urlpatterns = [
    path('register/', views.register_student, name='register_student'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),

    path('dashboard/', views.student_dashboard, name='student_dashboard'),

    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/submit/', views.submit_challenge, name='submit_challenge'),

    path('upload-project/', views.upload_project, name='upload_project'),
    path('my-projects/', views.my_projects, name='my_projects'),

    path('skill-fingerprint/', views.skill_fingerprint, name='skill_fingerprint'),
    path('skill-growth/', views.skill_growth_timeline, name='skill_growth_timeline'),

    path('skill-gap-analysis/', skill_gap_views.student_skill_gap_analysis, name='skill_gap_analysis'),

    path('portfolio/<str:username>/', views.public_student_portfolio, name='public_student_portfolio'),
    path('portfolio-settings/', views.portfolio_settings, name='portfolio_settings'),

    path('recruiter/login/', views.recruiter_login, name='recruiter_login'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),

    path('recruiter/student/<str:username>/assessment/', views.recruiter_student_assessment, name='recruiter_student_assessment'),

    path('recruiter/compare-students/', views.recruiter_compare_students, name='recruiter_compare_students'),

    path('recruiter/leaderboard/', leaderboard_views.student_leaderboard, name='student_leaderboard'),

    path('recruiter/logout/', views.recruiter_logout, name='recruiter_logout'),
]
