from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_channels, name='channels'),
    path('channel_posts/<int:channel_id>/', views.channel_posts, name='channel_posts'),
]
