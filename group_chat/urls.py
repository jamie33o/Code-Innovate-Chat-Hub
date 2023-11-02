from django.urls import path
from group_chat.views.channels_view import ChannelsView, AddUserToChannelView
from group_chat.views.posts_comments_view import PostsView, CommentsView
from group_chat.views.util_views import ImageUploadView, AddOrUpdateEmojiView



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
