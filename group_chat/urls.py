from django.urls import path
from .views import (ChannelsView, 
                    PostsView, 
                    CommentsView, 
                    AddUserToChannelView, 
                    ImageUploadView,
                    AddOrUpdateEmojiView,
                    )

urlpatterns = [
    path('', ChannelsView.as_view(), name='channels'),
    path('channel_posts/<int:channel_id>/', PostsView.as_view(), name='channel_posts'),
    path('channel_posts/<int:channel_id>/<int:post_id>/', PostsView.as_view(), name='channel_posts'),
    path('post_comments/<int:post_id>/', CommentsView.as_view(), name='post_comments'),
    path('add_user_to_channel/<int:channel_id>/<int:user_id>/', AddUserToChannelView.as_view(), name='add_user_to_channel'),
    path('upload-image/', ImageUploadView.as_view(), name='image_upload'),
    path('post_emoji/<int:id>/', AddOrUpdateEmojiView.as_view(), name='post_emoji'),
    path('comment_emoji/<int:id>', AddOrUpdateEmojiView.as_view(), name='comment_emoji'),

]
