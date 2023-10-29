from django.db import models
from django.contrib.auth import get_user_model

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    #image_url = models.URLField(max_length=1024, null=True, blank=True)
    last_viewed_channel_id = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return self.user.username
