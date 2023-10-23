from django.urls import path
from .views import (HomeView, 
                    ChannelPostsView, 
                    PostCommentsView, 
                    AddUserToChannelView, 
                    ImageUploadView,
                    AddOrUpdateEmojiView,
                    )

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('channel_posts/<int:channel_id>/', ChannelPostsView.as_view(), name='channel_posts'),
    path('post_comments/<int:post_id>/', PostCommentsView.as_view(), name='post_comments'),
    path('add_user_to_channel/<int:channel_id>/<int:user_id>/', AddUserToChannelView.as_view(), name='add_user_to_channel'),
    path('upload-image/', ImageUploadView.as_view(), name='image_upload'),
    path('post_emoji/<int:id>/', AddOrUpdateEmojiView.as_view(), name='post_emoji'),
    path('comment_emoji/<int:id>', AddOrUpdateEmojiView.as_view(), name='comment_emoji'),

]
