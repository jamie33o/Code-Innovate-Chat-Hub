# urls.py
from django.urls import path
from .views import InboxView, SendMessageView, MessageListView

urlpatterns = [
    path('', InboxView.as_view(), name='inbox'),
    path('send_message/<int:receiver_id>/', SendMessageView.as_view(), name='send_message'),
    path('message_list/<int:sender_id>/<int:receiver_id>/', MessageListView.as_view(), name='message_list'),

]
