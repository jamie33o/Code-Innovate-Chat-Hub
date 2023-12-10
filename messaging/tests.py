"""
Tests.py is for running automated tests
"""
from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Conversation, Message, ImageModel, EmojiModel


class BaseMessagingTestCase(TestCase):
    """
    Base test case for messaging-related tests.
    """

    def setUp(self):
        """
        Set up common test data.
        """
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.receiver = User.objects.create_user(username='testuser1', password='testpassword1')

    def create_conversation_and_message(self):
        """
        Create a conversation and a message for testing.

        Returns:
        - Tuple: A tuple containing the created conversation and message.
        """
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user, self.receiver)

        # Create a message in the conversation
        message = Message.objects.create(
            sender=self.user,
            receiver=self.receiver,
            content='Test message',
            timestamp=datetime.now(),
            conversation=conversation
        )

        return conversation, message


class InboxViewTest(BaseMessagingTestCase):
    """
    Test case for the InboxView.
    """
    def test_get_inbox_view(self):
        """
        Test the GET request for the inbox view.
        """
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Create a conversation and message
        conversation, message = self.create_conversation_and_message()

        # Call the InboxView
        response = self.client.get(reverse('inbox'))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the rendered context contains the expected data
        self.assertEqual(len(response.context['messages']), 1)
        self.assertEqual(response.context['messages'][0], message)
        # unread message is created in signals.py when a new message created
        self.assertEqual(len(response.context['unread_messages']), 1)
        self.assertEqual(response.context['unread_messages'][0], conversation.id)
        self.assertEqual(len(response.context['conversation_users']), 2)
        self.assertEqual(response.context['conversation_users'][0], self.user)

        # Check if the rendered template is correct
        self.assertTemplateUsed(response, 'messaging/inbox.html')


class MessageListViewTest(BaseMessagingTestCase):
    """
    Test case for the MessageListView.
    """

    def test_get_message_list_view(self):
        """
        Test the GET request for the message list view.
        """
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

         # Create a conversation and message
        conversation, message = self.create_conversation_and_message()

        # Call the MessageListView for the conversation
        response = self.client.get(reverse('message_list', args=[conversation.id]))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the rendered context contains the expected data
        self.assertEqual(len(response.context['messages']), 1)
        self.assertEqual(response.context['messages'][0], message)
        self.assertEqual(response.context['receiver'], self.receiver)
        self.assertEqual(response.context['conversation_id'], conversation.id)

        # Check if the rendered template is correct
        self.assertTemplateUsed(response, 'messaging/message-list.html')


    def test_post_message_list_view(self):
        """
        Test the POST request for the message list view.
        """
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Create a conversation and message
        conversation, _ = self.create_conversation_and_message()
    
        # Create a message content for the POST request
        message_content = 'New test message'

        # Call the MessageListView with a POST request to send a new message
        response = self.client.post(reverse('message_list',
                                            args=[conversation.id]),
                                    {'post': message_content})

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the message is created
        self.assertTrue(Message.objects.filter(content=message_content).exists())


class MessageDeleteViewTest(BaseMessagingTestCase):
  

    def test_delete_message_view(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Create a conversation and message
        _, message = self.create_conversation_and_message()

        # Get the URL for the MessageDeleteView with the message_id parameter
        url = reverse('delete_message', args=[message.id])


        # Make a DELETE request to delete the message
        response = self.client.delete(url)

        # Check if the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

        # Check if the message is deleted from the database
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=message.id)

        # Check the JSON response for success
        expected_response = {'status': 'success', 'message': 'Message deleted'}
        self.assertEqual(response.json(), expected_response)

    def test_delete_nonexistent_message_view(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Get a non-existent message_id
        nonexistent_message_id = 999

        # Get the URL for the MessageDeleteView with the non-existent message_id
        url = reverse('delete_message', args=[nonexistent_message_id])

        # Make a DELETE request to delete the non-existent message
        response = self.client.delete(url)

        # Check if the response status code is 404 (not found)
        self.assertEqual(response.status_code, 404)


class ConversationDeleteViewTest(BaseMessagingTestCase):

    def test_delete_conversation_view(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        # Create a conversation and message
        conversation, _ = self.create_conversation_and_message()
        # Get the URL for the ConversationDeleteView with the conversation_id parameter
        url = reverse('delete_conversation', args=[conversation.id])

        # Make a DELETE request to delete the conversation
        response = self.client.delete(url)

        # Check if the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

        # Check if the conversation is deleted from the database
        with self.assertRaises(Conversation.DoesNotExist):
            Conversation.objects.get(id=conversation.id)

        # Check the JSON response for success
        expected_response = {'status': 'success', 'message': 'Conversation deleted'}
        self.assertEqual(response.json(), expected_response)

    def test_delete_nonexistent_conversation_view(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Get a non-existent conversation_id
        nonexistent_conversation_id = 999

        # Get the URL for the ConversationDeleteView with the non-existent conversation_id
        url = reverse('delete_conversation', args=[nonexistent_conversation_id])

        # Make a DELETE request to delete the non-existent conversation
        response = self.client.delete(url)

        # Check if the response status code is 404 (not found)
        self.assertEqual(response.status_code, 404)



class ImageUploadViewTest(BaseMessagingTestCase):
   

    def test_upload_image_view(self):
        self.client.login(username='testuser', password='testpassword')

        # Create a sample image file for testing
        image_content = b'fake image content'
        image_file = SimpleUploadedFile("test_image.jpg", image_content)

        # Get the URL for the ImageUploadView
        url = reverse('image_upload')

        # Make a POST request to upload the image
        response = self.client.post(url, {'file': image_file})

        # Check if the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

        # Check if a new ImageModel instance is created
        self.assertTrue(ImageModel.objects.exists())

        # Check the JSON response for success
        new_image = ImageModel.objects.first()
        expected_response = {'status': 'Success', 'url': new_image.image.url}
        self.assertEqual(response.json(), expected_response)

    def test_upload_no_file_view(self):
        # Get the URL for the ImageUploadView
        url = reverse('image_upload')

        # Make a POST request without a file to simulate an error
        response = self.client.post(url)

        # Check if the response status code is 200 (success) or customize based on your requirements
        self.assertEqual(response.status_code, 400)

        # Check the JSON response for an error message
        expected_response = {'status': 'Error', 'message': 'Image could not be uploaded'}
        self.assertEqual(response.json(), expected_response)


