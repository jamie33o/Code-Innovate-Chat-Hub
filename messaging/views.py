# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from .models import Message, UnreadMessage
from django.utils.decorators import method_decorator
from django.db import models  
from django.db.models import Q
from datetime import datetime




@method_decorator(login_required, name='dispatch')
class InboxView(View):
    template_name = 'messaging/inbox.html'

    def get(self, request, receiver_id=None):
        # Retrieve received messages and unread messages for the user
        message_exists = None
            
        
        messages = Message.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('sender', 'receiver', '-timestamp').distinct('sender', 'receiver')

        unread_messages = UnreadMessage.objects.filter(user=request.user)

        if receiver_id:
            receiver= get_object_or_404(User, id=receiver_id)
            message_exists = any(receiver_id is message.sender.id or receiver_id is message.receiver.id for message in messages)
            if not message_exists:
                # Create a new Message object
                new_message = Message(
                    sender=request.user,  # Set the sender
                    receiver= receiver,
                    timestamp=datetime.now(),
                    content="New message!",
                )
        

                # Append the new_message object to the list
                messages = list(messages)
                messages.append(new_message)

        context = {
            'messages': messages,
            'unread_messages': unread_messages,
        }
        if not message_exists and receiver_id:
            context['new_message'] = True
        elif receiver_id:
            context['receiver'] = receiver

        return render(request, self.template_name, context)
    


@method_decorator(login_required, name='dispatch')
class MessageListView(View):
    template_name = 'messaging/message-list.html'

    def get(self, request, sender_id, receiver_id):
        sender = get_object_or_404(User, id=sender_id)
        receiver = get_object_or_404(User, id=receiver_id)

        # Retrieve messages between the sender and receiver
        messages = Message.objects.filter(
            (models.Q(sender=sender) & models.Q(receiver=receiver)) |
            (models.Q(sender=receiver) & models.Q(receiver=sender))
        ).order_by('timestamp')

        context = {
            'sender': sender,
            'receiver': receiver,
            'messages': messages,
        }
        # Mark unread messages as read
        # unread_messages.delete()
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class SendMessageView(View):
    template_name = 'messaging/send_message.html'

    def post(self, request, receiver_id):
        receiver = User.objects.get(pk=receiver_id)
        content = request.POST.get('content', '')

        if content:
            message = Message(sender=request.user, receiver=receiver, content=content)
            message.save()

        return redirect('inbox')


