# urls.py
from django.urls import path
from .views import InboxView, MessageListView, GenericObjectDeleteView

urlpatterns = [
    path('', InboxView.as_view(), name='inbox'),
    path('new_message/<int:receiver_id>/', 
         InboxView.as_view(), name='new_message'),
    path('send_message/<int:receiver_id>/', 
         MessageListView.as_view(), name='send_message'),
    path('message_list/<int:sender_id>/<int:receiver_id>/', 
         MessageListView.as_view(), name='message_list'),
    path('delete_obj/<str:model>/<int:pk>/',
         GenericObjectDeleteView.as_view(), name='delete_obj'),
]
