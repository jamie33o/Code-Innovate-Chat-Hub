# forms.py

from django import forms
from .models import UserProfile
from django.contrib.auth.forms import UserChangeForm


class StatusForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['status']
        STATUS_CHOICES = [
        ('active', 'Active'),
        ('away', 'Away'),
        ]

        is_active = forms.ChoiceField(choices=STATUS_CHOICES, label='Status')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].label = 'Set Status'
            

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
      
            


class EditProfileForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    

    class Meta:
        model = UserProfile
        fields = ['bio', 'linkedin', 'website', 'github', 'email', 'phone', 'mobile', 'location', 'password', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize labels to remove the colon for all fields
        for field_name, field in self.fields.items():
            field.label_suffix = ''
            field.widget.attrs['placeholder'] = f'Enter your {field_name}'
