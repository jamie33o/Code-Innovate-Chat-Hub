# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from .models import Message, UnreadMessage, Conversation
from django.utils.decorators import method_decorator
from django.db import models  
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from django.http import JsonResponse



@method_decorator(login_required, name='dispatch')
class InboxView(View):
    template_name = 'messaging/inbox.html'

    def get(self, request, receiver_id=None):
        # Retrieve received messages and unread messages for the user
        message_exists = False
        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)


        unread_messages = UnreadMessage.objects.filter(user=request.user)
        
        # Retrieve conversations involving the current user
        conversations = Conversation.objects.filter(participants=request.user)
    
        # Retrieve the messages in the conversation
        messages_by_conversation = []
        if conversations.exists():
            for conversation in conversations:
                # Retrieve the latest message in the conversation
                latest_message = conversation.messages.order_by('-timestamp').first()

                # Check if there is a latest message before adding it to the list
                if latest_message:
                    messages_by_conversation.append(latest_message)

                if receiver_id and receiver_id in conversation.participants.values_list('id', flat=True):
                    message_exists = True
        
        # Add participants to the conversation if not already there
        if receiver_id and not message_exists:
            # Create a temporary Message
            new_message = Message(
                sender=request.user,
                receiver=receiver,
                content='new message',
                timestamp=datetime.now(),
                conversation=Conversation()
            )

            messages_by_conversation.append(new_message)

        context = {
            'messages': messages_by_conversation,
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
        messages = None
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
            'messages' : None,
            'conversation_id': conversation.id
        }
        if messages:
            context['messages'] =  messages
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
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, receiver)
            # Create a new message
            message = Message(sender=request.user, receiver=receiver, content=content,conversation=conversation)
            message.save()

            html_content = render_to_string('messaging/single-message.html', {'message': message})
            self.broadcast_message(request, html_content, conversation.id, None)

         
        return redirect('inbox')


    def broadcast_message(self, request, instance_html, conversation_id, edit_id):
        """
        Broadcast a message to the channel layer.

        Args:
            request (HttpRequest): The HTTP request object.
            message_type (str): The type of message.
            message_content (str): The content of the message.
            instance_id (int): The ID of the instance.

        Returns:
            JsonResponse: JSON response indicating the status of the broadcast.
        """

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"messaging_{conversation_id}",
                {
                    'type': 'messaging_notification',
                    'message': 'New message added!',
                    'html': instance_html,
                    'created_by': request.user.username,
                    'edit_id': edit_id,
                }
            )
            return JsonResponse({'status': 'success', 'message': 'message sent'})
        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})

