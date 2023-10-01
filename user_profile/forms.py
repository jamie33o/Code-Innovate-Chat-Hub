# forms.py

from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'is_active', 'profile_picture']  # Add other fields as needed
