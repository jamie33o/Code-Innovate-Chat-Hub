from django.urls import path
from . import views
# urls to the views functions
urlpatterns = [
    path('', views.view_channels, name='channels'),
    path('channel_posts/<int:channel_id>/', views.view_channels , name='channel_posts'),
    path('add_user_to_channel/<int:channel_id>/<int:user_id>/', views.add_user_to_channel, name='add_user_to_channel'),

]
