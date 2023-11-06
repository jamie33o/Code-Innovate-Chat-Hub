from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

class ChannelModel(models.Model):
    """
    This class is for each indivual channel that is created 
    and the fields to be added in the the database

    Parameters:
        super class: class the this class inherits from
    """
    created_by = models.ForeignKey(get_user_model(),
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=True)
    name = models.CharField(max_length=254,default='')
    users = models.ManyToManyField(get_user_model(), related_name='channels')

    def __str__(self):
        return self.name
    
    @property
    def latest_post(self):
        return self.posts_created.latest('created_date')
    
    
class ChannelLastViewedModel(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    channel = models.ForeignKey(ChannelModel, on_delete=models.CASCADE)
    last_visit = models.DateTimeField(auto_now=True)

    
class ImageModel(models.Model):
    image = models.ImageField(upload_to='images/')

class EmojiModel(models.Model):
    emoji_colon_name = models.TextField(unique=False)
    users_who_incremented = models.ManyToManyField(get_user_model(), related_name='%(class)s_incremented', blank=True)

    def get_incremented_users(self):
        return self.users_who_incremented.all()

class PostsModel(models.Model):
    """
    This class is for each indivual post in a chanel

    Parameters:
        super class: class the this class inherits from
    """
    created_by = models.ForeignKey(get_user_model(),
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=254,default='')
    images = models.TextField(blank=True, default="")
    emojis = models.ManyToManyField(EmojiModel)

    post = models.TextField()
    post_channel = models.ForeignKey(
        ChannelModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts_created'
    )

    def get_image_urls(self):
        return [url.strip() for url in self.images.split(',') if url.strip()]
    
    @property
    def latest_comment(self):
        return self.comments_created.latest('created_date')
    


class CommentsModel(models.Model):
    """
    This class is for comments on each indivual post

    Parameters:
        super class: class the this class inherits from
    """
    created_by = models.ForeignKey(get_user_model(),
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='%(class)s_created')
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=254,default='')
    emojis = models.ManyToManyField(EmojiModel)
    images = models.TextField(blank=True, default="")


    post = models.TextField()

    comment_post = models.ForeignKey(
        PostsModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments_created'
    )

    def get_image_urls(self):
        return [url.strip() for url in self.images.split(',') if url.strip()]
    


class SavedPost(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(PostsModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
    

