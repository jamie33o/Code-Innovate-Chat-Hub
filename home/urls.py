from django.urls import path
from . import views
# urls to the views functions
urlpatterns = [
    path('', views.home_view, name='home'),
    path('channel_posts/<int:channel_id>/', views.home_view , name='channel_posts'),
    path('add_user_to_channel/<int:channel_id>/<int:user_id>/', views.add_user_to_channel, name='add_user_to_channel'),

]
