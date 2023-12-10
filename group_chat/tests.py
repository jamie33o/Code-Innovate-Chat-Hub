from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from group_chat.models import ChannelModel, PostsModel, CommentsModel
from messaging.models import UnreadMessage, Conversation


class ChannelsViewTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

    def test_channels_view_get(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Create a channel for testing
        channel = ChannelModel.objects.create(name='Test Channel', created_by=self.user)
        channel.users.add(self.user)

        # Get the URL for the ChannelsView
        url = reverse('channels')

        # Make a GET request to the ChannelsView
        response = self.client.get(url)

        # Check if the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

        # Check if the channel name is present in the response content
        self.assertContains(response, 'Test Channel')

        # Check if the user is in the channel users
        self.assertIn(self.user, channel.users.all())

        # Check if the last_viewed_channel_id is present in the context
        self.assertIn('last_viewed_channel_id', response.context)

    def test_add_user_to_channel_view_post(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Create a channel for testing
        channel = ChannelModel.objects.create(name='Test Channel')

        # Create another user for testing
        another_user = get_user_model().objects.create_user(username='anotheruser', password='testpassword')

        # Get the URL for the AddUserToChannelView
        url = reverse('add_user_to_channel', args=[channel.id, another_user.id])

        # Make a POST request to the AddUserToChannelView
        response = self.client.post(url)

        # Check if the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

        # Check if the user is added to the channel users
        self.assertIn(another_user, channel.users.all())

        # Check if the response contains success message
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'success')

    def test_add_user_to_channel_view_post_object_not_found(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Create a channel for testing
        channel = ChannelModel.objects.create(name='Test Channel')

        # Get the URL for the AddUserToChannelView with invalid user_id
        url = reverse('add_user_to_channel', args=[channel.id, 999])

        # Make a POST request to the AddUserToChannelView
        response = self.client.post(url)

        # Check if the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

        # Check if the response contains error message for object not found
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'Error')
        self.assertIn('Object not found', response.json()['message'])


class ChannelsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
         # Log in the user
        self.client.login(username='testuser', password='testpassword')
        self.channel = ChannelModel.objects.create(name='Test Channel')
        self.url = reverse('view_channel',  args=[self.channel.id])

    def test_get_channels_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_chat/home.html')

    def test_add_user_to_channel_view(self):
        another_user = get_user_model().objects.create_user(username='anotheruser', password='testpassword')
        url_add_user = reverse('add_user_to_channel', args=[self.channel.id, another_user.id])
        response = self.client.post(url_add_user)
        self.assertEqual(response.status_code, 200)
        self.assertIn(another_user, self.channel.users.all())

class PostsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
         # Log in the user
        self.client.login(username='testuser', password='testpassword')
        self.channel = ChannelModel.objects.create(name='Test Channel')
        self.url = reverse('channel_posts', args=[self.channel.id])

    def test_get_posts_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_chat/posts.html')

    def test_get_posts_view_with_pagination(self):
        for i in range(15):  # Creating 15 posts
            PostsModel.objects.create(created_by=self.user, post=f'Test post {i}', post_channel=self.channel)

        response = self.client.get(self.url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_chat/paginated-posts.html')

    def test_post_to_posts_view(self):
        post_data = {'post': 'Test post content'}
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostsModel.objects.count(), 1)

    def test_post_to_posts_view_with_existing_post_id(self):
        existing_post = PostsModel.objects.create(created_by=self.user, post='Existing post', post_channel=self.channel)
        post_data = {'post': 'Updated post content'}
        url_with_post_id = reverse('channel_posts', args=[self.channel.id, existing_post.id])
        response = self.client.post(url_with_post_id, post_data)
        self.assertEqual(response.status_code, 200)

class CommentsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.channel = ChannelModel.objects.create(name='Test Channel')
        self.post = PostsModel.objects.create(created_by=self.user, post='Test post', post_channel=self.channel)
        self.url = reverse('post_comments', args=[self.post.id])

    def test_get_comments_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_chat/comments.html')

    def test_post_to_comments_view(self):
        comment_data = {'post': 'Test comment content'}
        response = self.client.post(self.url, comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CommentsModel.objects.count(), 1)
