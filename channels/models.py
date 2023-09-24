from django.db import models
from django.contrib.auth.models import User

class ChannelModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=True)
    name = models.CharField(max_length=254,default='')
    description = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return self.name
    

class ChannelPosts(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=254,default='')
    post = models.TextField(blank=True, null=True)
    # ForeignKey to associate posts with channels
    post_channel = models.ForeignKey(
        ChannelModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts_created'
    )



