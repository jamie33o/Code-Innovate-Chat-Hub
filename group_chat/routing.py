"""
Routing configuration for WebSocket consumers in the group_chat app.

This module defines the WebSocket URL patterns for connecting to
different consumers, such as `PostConsumer` for handling channel posts
and `CommentConsumer` for handling post comments.

WebSocket URL Patterns:
- ws/channel_posts/(?P<channel_id>\d+)/$: Connects to `PostConsumer` for channel posts.
- ws/post_comments/(?P<post_id>\d+)/$: Connects to `CommentConsumer` for post comments.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/channel_posts/(?P<channel_id>\d+)/$', consumers.PostConsumer.as_asgi()),
    re_path(r'ws/post_comments/(?P<post_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
]
