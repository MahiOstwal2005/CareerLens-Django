from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'college', 'program', 'semester', 'skills', 'areas_of_interest', 'portfolio_url', 'resume_link', 'email_notifications', 'dark_mode']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'college': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., University of Science'}),
            'program': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., B.S. Computer Science'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Django, React, etc.'}),
            'areas_of_interest': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Web Development, Data Science, etc.'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.com'}),
            'resume_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to Google Drive / PDF'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
