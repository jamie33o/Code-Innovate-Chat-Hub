from django.db import models
from django.contrib.auth.models import User


class ChannelModel(models.Model):
    """
    This class is for each indivual channel that is created 
    and the fields to be added in the the database

    Parameters:
        super class: class the this class inherits from
    """
    created_by = models.ForeignKey(User,
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=True)
    name = models.CharField(max_length=254,default='')
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='channels')

    def __str__(self):
        return self.name


class ChannelPosts(models.Model):
    """
    This class is for each indivual post in a chanel

    Parameters:
        super class: class the this class inherits from
    """
    created_by = models.ForeignKey(User,
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=254,default='')
    # Supports rich text, including images
    # ForeignKey to associate posts with channel
    post = models.TextField()

    post_channel = models.ForeignKey(
        ChannelModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts_created'
    )
