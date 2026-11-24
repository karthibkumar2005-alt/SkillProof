
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import StudentProfile, ProjectEvidence


class StudentRegistrationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )

    college_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your college name'
        })
    )

    department = forms.ChoiceField(
        choices=StudentProfile.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    graduation_year = forms.IntegerField(
        min_value=2020,
        max_value=2035,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Graduation year'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# PROJECT EVIDENCE FORM
class ProjectEvidenceForm(forms.ModelForm):

    class Meta:
        model = ProjectEvidence

        fields = [
            'project_title',
            'description',
            'github_link',
            'project_report',
            'project_screenshot'
        ]

        widgets = {
            'project_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your project',
                'rows': 5
            }),

            'github_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username/project'
            })
        }
