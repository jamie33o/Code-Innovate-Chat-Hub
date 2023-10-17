from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/channel_posts/(?P<channel_id>\d+)/$', consumers.PostConsumer.as_asgi()),
    re_path(r'ws/post_comments/(?P<post_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
]
