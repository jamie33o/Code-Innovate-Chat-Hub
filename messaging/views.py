# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from .models import Message, UnreadMessage, Conversation
from django.utils.decorators import method_decorator
from django.db import models  
from datetime import datetime



@method_decorator(login_required, name='dispatch')
class InboxView(View):
    template_name = 'messaging/inbox.html'

    def get(self, request, receiver_id=None):
        # Retrieve received messages and unread messages for the user
        message_exists = True

        unread_messages = UnreadMessage.objects.filter(user=request.user)
        
        # Retrieve conversations involving the current user
        conversations = Conversation.objects.filter(participants=request.user)
        
        if not conversations.exists():
            # Create a new conversation if none exists
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user)
        else:
            # Use the first existing conversation
            conversation = conversations.first()

        # Retrieve the messages in the conversation
        messages_by_conversation = []

        # Retrieve the latest message in the conversation
        latest_message = conversation.messages.order_by('-timestamp').first()

        # Check if there is a latest message before adding it to the list
        if latest_message:
            messages_by_conversation.append(latest_message)

        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)

            # Add participants to the conversation if not already there
            if receiver not in conversation.participants.all():
                conversation.participants.add(receiver)

            # Create a new Message
            new_message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content='new message',
                timestamp=datetime.now(),
                conversation=conversation
            )

            messages_by_conversation.append(new_message)

        context = {
            'messages': messages_by_conversation,
            'unread_messages': unread_messages,
        }

        if message_exists and receiver_id:
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

        # Find the conversation involving both the sender and receiver
        conversation = Conversation.objects.filter(participants=request.user).filter(participants=receiver).first()

        # Check if the conversation exists
        if conversation:
            # Retrieve messages in the conversation and order by timestamp
            messages = conversation.messages.all().order_by('timestamp')

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

    def post(self, request, receiver_id):
        receiver = User.objects.get(pk=receiver_id)
        content = request.POST.get('post', '')
        if content:
            conversation = Conversation.objects.filter(participants=request.user).filter(participants=receiver).first()

            # Create a new message
            message = Message(sender=request.user, receiver=receiver, content=content,conversation=conversation)
            message.save()

         
        return redirect('inbox')


