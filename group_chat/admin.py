"""
Django administration configuration for the 'group_chat' app.

Registers the Models for administration.

"""

from django.contrib import admin
from .models import ChannelModel,CommentsModel,PostsModel

admin.site.register(ChannelModel)
admin.site.register(PostsModel)
admin.site.register(CommentsModel)
