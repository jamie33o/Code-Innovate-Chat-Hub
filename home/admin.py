from django.contrib import admin
from .models import ChannelModel,PostComments,ChannelPosts

admin.site.register(ChannelModel)
admin.site.register(PostComments)
admin.site.register(ChannelPosts)
