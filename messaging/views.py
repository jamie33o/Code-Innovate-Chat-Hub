"""
this module is for messaging views
"""
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, UnreadMessage, Conversation, ImageModel

# pylint: disable=no-member

@method_decorator(login_required, name='dispatch')
class InboxView(View):
    """
    View for displaying the user's inbox with conversations and messages.

    Attributes:
    - template_name (str): The template to render for the inbox view.
    """
    template_name = 'messaging/inbox.html'

    def get(self, request, receiver_id=None):
        """
        Handle GET requests to retrieve and display the user's inbox.

        Parameters:
        - request (HttpRequest): The request object.
        - receiver_id (int, optional): The ID of the receiver user for starting a new conversation.

        Returns:
        - HttpResponse: Rendered inbox template with relevant context.
        """
        try:
            # Retrieve received messages and unread messages for the user
            message_exists = False
            if receiver_id:
                receiver = get_object_or_404(User, id=receiver_id)

            # Retrieve conversations involving the current user
            conversations = Conversation.objects.filter(participants=request.user)

            conversation_users = User.objects.filter(conversation__in=conversations).distinct()

            unread_messages = UnreadMessage.objects.filter(conversation__participants=request.user)\
                                                    .values_list('conversation', flat=True)


            # Retrieve the messages in the conversation
            messages_by_conversation = []
            if conversations.exists():
                for conversation in conversations:
                    # Retrieve the latest message in the conversation
                    latest_message = conversation.messages.order_by('-timestamp').first()

                    # Check if there is a latest message before adding it to the list
                    if latest_message:
                        messages_by_conversation.append(latest_message)

                    if (
                        receiver_id and
                        receiver_id in conversation.participants.values_list('id', flat=True) and
                        latest_message
                    ):
                        message_exists = True

            # Add participants to the conversation if not already there
            if receiver_id and not message_exists:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, receiver)
                # Create a temporary Message
                new_message = Message(
                    sender=request.user,
                    receiver=receiver,
                    content='new message',
                    timestamp=datetime.now(),
                    conversation=conversation
                )
                conversation.save()

                messages_by_conversation.append(new_message)

            context = {
                'messages': messages_by_conversation,
                'unread_messages': unread_messages,
                'conversation_users': conversation_users
            }

            if not message_exists and receiver_id:
                context['new_message'] = True
            elif receiver_id:
                context['receiver'] = receiver

            return render(request, self.template_name, context)
        except Exception as e:
            return JsonResponse({'status': 'Error', 'message': f"Error retreiving conversations: {e}"}, status=500 )



@method_decorator(login_required, name='dispatch')
class MessageListView(View):
    """
    View for displaying a list of messages in a conversation.

    Attributes:
    - template_name (str): The template to render for the message list view.
    """
    template_name = 'messaging/message-list.html'

    def get(self, request, conversation_id):
        """
        Handle GET requests to retrieve and display the list of messages in a conversation.

        Parameters:
        - request (HttpRequest): The request object.
        - conversation_id (int): The ID of the conversation.

        Returns:
        - HttpResponse: Rendered message list template with relevant context.
        """
        try:
            messages = None
            # Find the conversation involving both the sender and receiver
            conversation = get_object_or_404(Conversation, id=conversation_id)

            # Get the receiver excluding the current user from participants
            receiver = conversation.participants.exclude(id=request.user.id).first()

            
            # Retrieve messages in the conversation and order by timestamp
            messages = conversation.messages.all().order_by('timestamp')

            UnreadMessage.objects.filter(conversation=conversation).delete()

            context = {
                'receiver': receiver,
                'messages' : None,
                'conversation_id': conversation.id
            }

            if messages:
                context['messages'] =  messages
         
            return render(request, self.template_name, context)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Conversation does not exist!! Error: {e}'}, status=500)


    def post(self, request, conversation_id=None, message_id=None):
        """
        Handle POST requests to send or update a message in a conversation.

        Parameters:
        - request (HttpRequest): The request object.
        - receiver_id (int, optional): The ID of the receiver user.
        - message_id (int, optional): The ID of the message to be updated.

        Returns:
        - JsonResponse: JSON response indicating the status of the request.
        """
        try:
            content = request.POST.get('post', '')
            url_list = request.POST.getlist('urls[]')
            images = ",".join(url_list)
           
            conversation = get_object_or_404(Conversation, id=conversation_id)
            receiver = conversation.participants.exclude(id=request.user.id).first()

            if not message_id:
                message = Message(sender=request.user,
                                  receiver=receiver,
                                  content=content,
                                  images=images,
                                  conversation=conversation)
            else:
                message = get_object_or_404(Message, id=message_id)
                message.content = content
                message.images = images

            message.save()

            context = {
                'sender': message.sender,
                'receiver': receiver,
                'message' : message,
                'conversation_id': conversation.id,
                'user': request.user,
            }

            html_content = render_to_string('messaging/single-message.html', context)
            self.broadcast_message(request, html_content, conversation.id, message_id)
            self.notification_msg(request, message.timestamp,
                                  message.content, 'conversation',
                                  conversation.id)

            return JsonResponse({'status': 'success'}, status= 200)
        except Exception as e:
            print(f"Error in MessageListView post request: {e}")

            return JsonResponse({'status': 500, 'error': 'Internal Server Error'})


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
            
        except Exception as e:
            # Handle unexpected exceptions
            print({'status': 'error', 'message': str(e)})


    def notification_msg(self, request, timestamp, message, model_name, model_id):
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
        formatted_time = timestamp.strftime('%H:%M')
        try:
            channel_layer = get_channel_layer()
            context = {
                'type': 'global_consumer',
                'timestamp': formatted_time,
                'message': message,
                'created_by': request.user.username,
                'img_url': 'static/noimage.png',
                'model_id': model_id,
                'model_name': model_name,
            }
            if request.user.userprofile.profile_picture:
                context['img_url'] = request.user.userprofile.profile_picture.url
            async_to_sync(channel_layer.group_send)("global_consumer", context)

            return JsonResponse({'status': 'success', 'message': 'message sent'})
        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})



class MessageDeleteView(View):
    def delete(self, request, message_id):
        try:
            # Retrieve the message to be deleted
            message = get_object_or_404(Message, id=message_id)

            # Delete the message
            message.delete()

            # Return a JSON response indicating success
            return JsonResponse({'status': 'success', 'message': 'Message deleted'})
        except Exception as e:
            # Handle exceptions
            return JsonResponse({'status': 'error', 'message': f'Error deleting message: {str(e)}'}, status=404)

class ConversationDeleteView(View):
    def delete(self, request, conversation_id):
        try:
            # Retrieve the message to be deleted
            conversation = get_object_or_404(Conversation, id=conversation_id)

            # Delete the message
            conversation.delete()

            # Return a JSON response indicating success
            return JsonResponse({'status': 'success', 'message': 'Conversation deleted'},status=200)
        except Exception as e:
            # Handle exceptions
            return JsonResponse({'status': 'error', 'message': f'Error deleting conversation: {str(e)}'}, status=404)


class ImageUploadView(View):
    """
    View class for handling image uploads.
    """
    def post(self, request):
        """
        Handle POST requests to upload an image.

        Args:
            request (HttpRequest): The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            JsonResponse: JSON response indicating the status of the image upload.
        """
        try:
            if request.FILES.get('file'):
                image_file = request.FILES['file']

                # Create a new ImageModel instance
                new_image = ImageModel.objects.create(image=image_file)

                # Return the URL
                return JsonResponse({'status':'Success', 'url': new_image.image.url}, status=200)

            return JsonResponse({'status': 'Error', 'message': 'Image could not be uploaded'},status=400)
        except Exception as e:
            # Handle exceptions (e.g., database error, unexpected error)
            return JsonResponse({'status': 'Error', 'message': f'Error uploading image: {str(e)}'}, staus=500)


class AddOrUpdateEmojiView(View):
    """
    View class for adding or updating an emoji in a message model instance. 
    """
    def post(self, request, instance_id, *args, **kwargs):
        """
        Handle POST requests to add or update an emoji in message model instance.

        Args:
            request (HttpRequest): The HTTP request object.
            instance_id (int): The ID of the model instance.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            JsonResponse: JSON response indicating the status of the operation.
        """
        try:
            user = request.user
            emoji_colon_name = request.POST.get('emoji_colon_name')


            message_model = get_object_or_404(Message, pk=instance_id)

            # If it exists, increment the count and add the user
            instance, created = message_model.emojis.get_or_create(
                emoji_colon_name=emoji_colon_name,
                defaults={'emoji_colon_name': emoji_colon_name}
            )

            if created:
                # If a new instance is created, add the user
                instance.incremented_by.add(user)
                return JsonResponse({'status': 'added'}, status=200)

            # Check if the EmojiModel exists
            if request.user in instance.incremented_by.all():
                instance.incremented_by.remove(user)
                # Check if there are no more users and remove the instance if true
                if instance.incremented_by.count() == 0:
                    message_model.emojis.remove(instance)
                    return JsonResponse({'status': 'removed'}, status=200)
                return JsonResponse({'status': 'decremented'}, status=200)

            # If it exists, increment the count and add the user
            instance.incremented_by.add(user)
            return JsonResponse({'status': 'incremented'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

