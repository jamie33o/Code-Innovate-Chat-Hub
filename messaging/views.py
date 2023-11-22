# views.py
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import DeleteView
from django.apps import apps
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, UnreadMessage, Conversation




@method_decorator(login_required, name='dispatch')
class InboxView(View):
    template_name = 'messaging/inbox.html'

    def get(self, request, receiver_id=None):
        # Retrieve received messages and unread messages for the user
        message_exists = False
        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)


        #unread_messages = UnreadMessage.objects.filter(user=request.user)
        
        # Retrieve conversations involving the current user
        conversations = Conversation.objects.filter(participants=request.user)

        unread_messages = UnreadMessage.objects.filter(conversation__participants=request.user).values_list('conversation', flat=True)

    
        # Retrieve the messages in the conversation
        messages_by_conversation = []
        if conversations.exists():
            for conversation in conversations:
                # Retrieve the latest message in the conversation
                latest_message = conversation.messages.order_by('-timestamp').first()

                # Check if there is a latest message before adding it to the list
                if latest_message:
                    messages_by_conversation.append(latest_message)

                if receiver_id and receiver_id in conversation.participants.values_list('id', flat=True) and latest_message:
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
            'unread_messages': unread_messages
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
        conversation = self.get_conversation(sender, receiver)

        # Check if the conversation exists
        if conversation:
            # Retrieve messages in the conversation and order by timestamp
            messages = conversation.messages.all().order_by('timestamp')
            UnreadMessage.objects.filter(conversation=conversation).delete()
        
        if not conversation and receiver_id:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, receiver)

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

    def post(self, request, receiver_id):
        receiver = User.objects.get(pk=receiver_id)
        content = request.POST.get('post', '')
        if content:
            conversation = self.get_conversation(request.user, receiver)
            
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

    def get_conversation(self, user1, user2):
        conversation = Conversation.objects.filter(participants=user1).filter(participants=user2).first()
        return conversation
    

class GenericObjectDeleteView(DeleteView):
    """
    View class for deleting a generic object based on the URL parameters.
    """

    def get_object(self, queryset=None):
        """
        Retrieve the object to be deleted based on the URL parameters.

        Args:
            queryset: The queryset to use for retrieving the object.

        Returns:
            Model: The object to be deleted.
        """
        try:
            # Get the model class based on the URL parameter
            model_name = self.kwargs['model']
            model = apps.get_model(app_label='messaging', model_name=model_name)

            # Get the object to be deleted
            obj_pk = self.kwargs['pk']
            obj = get_object_or_404(model, pk=obj_pk)
            print(obj)

            return obj
        except (LookupError, ValueError, KeyError) as e:
            # Handle lookup errors, value errors, or key errors
            return JsonResponse({'status': 'error',
                                 'message': f'Error retrieving object: {str(e)}'})

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests to delete an object.

        Args:
            request (HttpRequest): The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            JsonResponse: JSON response indicating the status of the operation.
        """
        try:
            # Get the object to be deleted
            obj = self.get_object()
            model_name = obj.__class__.__name__

            # Delete the object
            obj.delete()

            # Override the delete method to return a JSON response
            return JsonResponse({'status': 'success', 'message': f'{model_name} deleted'})
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'status': 'error', 'message': f'Error deleting object: {str(e)}'})

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the template.

        Returns:
            dict: A dictionary containing context data.
        """
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.kwargs['model']
        return context