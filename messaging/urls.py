"""
URL patterns for messaging app.

These patterns define the routing for various views in the messaging app,
including the inbox, message list, new message, send message, edit message,
delete object, image upload, and messages emoji.

Attributes:
- urlpatterns (list): A list of URL patterns for the messaging app views.
"""
from django.urls import path
from .views import InboxView, MessageListView, GenericObjectDeleteView, ImageUploadView, AddOrUpdateEmojiView

urlpatterns = [
     path('', InboxView.as_view(), name='inbox'),
     path('new_message/<int:receiver_id>/', 
          InboxView.as_view(), name='new_message'),
     path('send_message/<int:receiver_id>/', 
          MessageListView.as_view(), name='send_message'),
     path('message_list/<int:sender_id>/<int:receiver_id>/',
          MessageListView.as_view(), name='message_list'),
     path('edit_message/<int:receiver_id>/<int:message_id>/',
          MessageListView.as_view(), name='edit_message'),
     path('delete_obj/<str:model>/<int:pk>/',
          GenericObjectDeleteView.as_view(), name='delete_obj'),
     path('upload-image/', ImageUploadView.as_view(), name='image_upload'),
     path('messages_emoji/<int:instance_id>/',
          AddOrUpdateEmojiView.as_view(), name='messages_emoji'),
]
