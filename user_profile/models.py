from django.db import models
from django.contrib.auth import get_user_model


class UserProfile(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('away', 'Away'),
    ]
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    username = models.CharField(max_length=255, blank=True, null=True)  # Add this line
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    last_viewed_channel_id = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    github = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

