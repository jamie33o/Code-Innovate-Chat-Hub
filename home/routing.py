from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/home/(?P<channel_id>\d+)/$', consumers.PostConsumer.as_asgi()),
]
