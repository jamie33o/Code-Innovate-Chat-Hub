"""
this module is for messaging views
"""
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import DeleteView
from django.apps import apps
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import boto3
from botocore.exceptions import NoCredentialsError
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


            #unread_messages = UnreadMessage.objects.filter(user=request.user)

            # Retrieve conversations involving the current user
            conversations = Conversation.objects.filter(participants=request.user)

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
                'conversation_users': conversation_users
            }

            if not message_exists and receiver_id:
                context['new_message'] = True
            elif receiver_id:
                context['receiver'] = receiver

            return render(request, self.template_name, context)
        except Exception as e:
            print(f"Error in InboxView GET request: {e}")



@method_decorator(login_required, name='dispatch')
class MessageListView(View):
    """
    View for displaying a list of messages in a conversation.

    Attributes:
    - template_name (str): The template to render for the message list view.
    """
    template_name = 'messaging/message-list.html'

    def get(self, request, sender_id, receiver_id):
        """
        Handle GET requests to retrieve and display the list of messages in a conversation.

        Parameters:
        - request (HttpRequest): The request object.
        - sender_id (int): The ID of the sender user.
        - receiver_id (int): The ID of the receiver user.

        Returns:
        - HttpResponse: Rendered message list template with relevant context.
        """
        try:
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
         
            return render(request, self.template_name, context)
        except Exception as e:
            print(f"Error in MessageListView GET request: {e}")

            return render(request, 'messaging/error.html')  # Render an error page

    def post(self, request, receiver_id=None, message_id=None):
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
            receiver = User.objects.get(pk=receiver_id)
            conversation = self.get_conversation(request.user, receiver)
            if not message_id and receiver_id:
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

            html_content = render_to_string('messaging/single-message.html', {'message': message})
            self.broadcast_message(request, html_content, conversation.id, message_id)
            self.notification_msg(request, message.timestamp,
                                  message.content, 'conversation',
                                  conversation.id)

            return JsonResponse({'status': 200})
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
            return JsonResponse({'status': 'success', 'message': 'message sent'})
        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get_conversation(self, user1, user2):
        """
        Retrieve a conversation between two users.

        Parameters:
        - user1: The first user.
        - user2: The second user.

        Returns:
        - Conversation or None: The Conversation object if found, or None if not found.
        """
        conversation = Conversation.objects.filter(participants=user1)\
                                            .filter(participants=user2).first()
        return conversation


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
            async_to_sync(channel_layer.group_send)(
                    "global_consumer",
                {
                    'type': 'global_consumer',
                    'timestamp': formatted_time,
                    'message': message,
                    'created_by': request.user.username,
                    'img_url': request.user.userprofile.profile_picture.url,
                    'model_id': model_id,
                    'model_name': model_name,
                }
            )
            return JsonResponse({'status': 'success', 'message': 'message sent'})
        except Exception as e:
            print(e)
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})



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
            if obj.images:
                url_list = obj.images.split(",")
                for image in url_list:
                    delete_image_from_s3(image)

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


def delete_image_from_s3(image_key):
    """
    Delete an image from an S3 bucket.

    Parameters:
    - image_key (str): The key or path of the image to be deleted from the S3 bucket.

    Returns:
    - bool: True if the image was successfully deleted, False otherwise.

    Raises:
    - NoCredentialsError: If AWS credentials are not available.
    """

    try:
        # Create an S3 client with the provided AWS credentials
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # Get the name of the S3 bucket from Django settings
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        # Delete the specified object (image) from the S3 bucket
        s3.delete_object(Bucket=bucket_name, Key=image_key)

        # Return True to indicate successful deletion
        return True

    except NoCredentialsError:
        # Handle the case when AWS credentials are not available
        print('Credentials not available')
        return False

    except Exception as e:
        # Handle other exceptions and print an error message
        print(f"Error deleting image from S3: {e}")
        return False


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
                return JsonResponse({'url': new_image.image.url})

            return JsonResponse({'status': 'Error', 'message': 'Image could not be uploaded'})
        except Exception as e:
            # Handle exceptions (e.g., database error, unexpected error)
            return JsonResponse({'status': 'Error', 'message': f'Error uploading image: {str(e)}'})


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
                return JsonResponse({'status': 'added'})

            # Check if the EmojiModel exists
            if request.user in instance.incremented_by.all():
                instance.incremented_by.remove(user)
                # Check if there are no more users and remove the instance if true
                if instance.incremented_by.count() == 0:
                    message_model.emojis.remove(instance)
                    return JsonResponse({'status': 'removed'})
                return JsonResponse({'status': 'decremented'})

            # If it exists, increment the count and add the user
            instance.incremented_by.add(user)
            return JsonResponse({'status': 'incremented'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
