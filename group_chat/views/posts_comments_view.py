import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user_profile.models import UserProfile
from group_chat.models import ChannelModel, PostsModel, ChannelLastViewedModel, CommentsModel
from group_chat.forms import PostsForm, CommentsForm
from django.template.loader import render_to_string


# pylint: disable=no-member


class BaseChatView(View):
    """
    Base class for chat views.
    """
    template_name = None  # Set this in the subclass

    def process_and_save(self, request, form):
        """
        Process and save the form instance.

        Args:
            request (HttpRequest): The HTTP request object.
            form (ModelForm): The form instance to be processed and saved.

        Returns:
            Model: The saved instance.
        """
        try:
            instance = form.save(commit=False)
            url_list = request.POST.getlist('urls[]')
            instance.images = ",".join(url_list)
            # allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
            # allowed_attributes = {'*': ['style', 'src', 'href']}
            # instance.post = bleach.clean(instance.post, tags=allowed_tags, attributes=allowed_attributes)
            instance.created_by = request.user
            instance.save()

            return instance
        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})

    def broadcast_message(self, request, message_type, instance_html, instance_id):
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
        print('working')

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"{message_type}_{instance_id}",
                {
                    'type': f'{message_type}_notification',
                    'message': f'New {message_type} added!',
                    'html': instance_html,
                    'created_by': request.user.username,
                }
            )
            return JsonResponse({'status': 'success', 'message': 'message sent'})
        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})


@method_decorator(login_required, name='dispatch')
class PostsView(BaseChatView):
    """
    View class for handling posts in a channel.
    """
    posts_template = 'group_chat/posts.html'
    paginated_template ='group_chat/paginated-posts.html'
    posts_per_page = 10
    single_post_template = 'group_chat/single-post.html'

    def get_channel(self, channel_id):
        """
        Retrieve the channel based on the channel ID.

        Args:
            channel_id (int): The ID of the channel.

        Returns:
            ChannelModel: The channel instance.
        """
        return get_object_or_404(ChannelModel, id=channel_id)

    def get_posts(self, channel):
        """
        Retrieve posts for a specific channel.

        Args:
            channel (ChannelModel): The channel instance.

        Returns:
            QuerySet: Queryset of posts for the channel.
        """
        return PostsModel.objects.filter(post_channel=channel).order_by('created_date')

    def get_paginated_posts(self, posts, page):
        """
        Paginate the list of posts.

        Args:
            posts (QuerySet): Queryset of posts.
            page (int): The requested page number.

        Returns:
            tuple: Paginated posts and the previous page number.
        """
        paginator = Paginator(posts, self.posts_per_page)
        total_pages = paginator.num_pages

        page = total_pages if not page else page

        try:
            # Start from the last page and go backward
            paginated_posts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
             # If the page is not an integer, show the last page
            paginated_posts = paginator.page(total_pages)

        prev_page_number = (
            paginated_posts.previous_page_number()
            if paginated_posts.has_previous()
            else None
        )
        return paginated_posts, prev_page_number


    def update_user_status(self, request, channel):
        """
        Update the user's last viewed status for a specific channel.

        Args:
            request (HttpRequest): The HTTP request object.
            channel (ChannelModel): The channel instance.
        """
        user_status, _ = ChannelLastViewedModel.objects.get_or_create(
            user=request.user,
            channel=channel
        )
        user_status.last_visit = timezone.now()
        user_status.save()

    def get(self, request, channel_id):
        """
        Handle GET requests to display posts in a channel.

        Args:
            request (HttpRequest): The HTTP request object.
            channel_id (int): The ID of the channel.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered HTML template with posts.
        """
        try:
            channel = self.get_channel(channel_id)
            posts = self.get_posts(channel)

            page = int(request.GET.get('page')) if request.GET.get('page') else None
            paginated_posts, next_page_num = self.get_paginated_posts(posts, page)

            post_comments_users = self.users_that_commented(paginated_posts)

            if request.user in channel.users.all():
                self.update_user_status(request, channel_id)

            form = PostsForm()

            context = {
                'channel': channel,
                'posts': paginated_posts,
                'form': form,
                'channel_users': channel.users.all(),
                'next_page_number': next_page_num,
                'post_comments_users': post_comments_users
            }

            if page:
                return render(request, self.paginated_template, context)

            return render(request, self.posts_template, context)

        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request, channel_id, post_id=None):
        """
        Handle POST requests to submit or update posts in a channel.

        Args:
            request (HttpRequest): The HTTP request object.
            channel_id (int): The ID of the channel.
            post_id (int): The ID of the post (if editing an existing post).
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Redirect or JSON response 
            based on the success or failure of the operation.
        """
        try:
            # If post_id is None, it's a new post; otherwise, it's an edit
            if post_id is None:
                form = PostsForm(request.POST)
            else:
                post = get_object_or_404(PostsModel, id=post_id)
                form = PostsForm(request.POST, instance=post)

            if form.is_valid():
                form.instance.post_channel = get_object_or_404(ChannelModel, id=channel_id)
                post = self.process_and_save(request, form)
                context = {
                    'channel': form.instance.post_channel,
                    'single_post': post,
                    'form': form,
                }

                try:
                    html_content = render_to_string(self.single_post_template, context)
                except Exception as e:
                    print(f"Error rendering template: {e}")

                self.broadcast_message(request, 'post', html_content, channel_id)

                if post_id is None:
                    redirect_url = reverse('channel_posts', args=[channel_id])
                    return redirect(redirect_url)

                # if its an edited post post_id will not be none
                # and edited post will be returned
                response_data = {
                    'status': 'success',
                    'post': post.post,
                    'images': None,
                }

                if post.images:
                    response_data['images'] = post.images
                return JsonResponse(response_data)


            # Return JSON response with validation errors
            return JsonResponse({'status': 'Error', 'message': form.errors})

        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)

    def update_last_viewed_channel(self, request, channel_id):
        """
        Update the last viewed channel for the user in their profile.

        Args:
            request (HttpRequest): The HTTP request object.
            channel_id (int): The ID of the channel.
        """
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.last_viewed_channel_id = channel_id
        user_profile.save()

    def users_that_commented(self, paginated_posts):
        """
        Retrieve information about users who commented on each post.

        Args:
            paginated_posts (Page): Paginated posts.

        Returns:
            dict: Dictionary containing information 
            about users who commented on each post.
        """
        users_that_commented = {}

        for post in paginated_posts:
            # Get the comments for the current post
            comments = post.comments_created.all()

            # Extract user IDs of users who have commented on the post
            commented_users_ids = comments.values_list('created_by', flat=True)

            # Retrieve additional information about the users
            commented_users_info = get_user_model().objects.filter(id__in=commented_users_ids)

            # Create a dictionary with user information for each post
            users_that_commented[post.id] = {
                'post': post,
                'commented_users': commented_users_info,
            }

        return users_that_commented


@method_decorator(login_required, name='dispatch')
class CommentsView(BaseChatView):
    """
    View class for handling comments.
    """
    comments_template = 'group_chat/comments.html'
    single_comment_template = 'group_chat/single-comment.html'

    def get(self, request, post_id):
        """
        Handle GET requests to display comments.

        Args:
            request (HttpRequest): The HTTP request object.
            post_id (int): The ID of the post.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered HTML template with comments.
        """
        post = get_object_or_404(PostsModel, id=post_id)
        comments = CommentsModel.objects.filter(comment_post=post)

        form = CommentsForm()

        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }

        return render(request, self.comments_template, context)

    def post(self, request, post_id, comment_id=None):
        """
        Handle POST requests to submit or update comments on a post.

        Args:
            request (HttpRequest): The HTTP request object.
            post_id (int): The ID of the post.
            comment_id (int): The ID of the comment (if editing an existing comment).
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Redirect or JSON response based on the success or failure 
            of the operation.
        """
        try:
            if comment_id is None:
                form = CommentsForm(request.POST)
            else:
                comment_model = get_object_or_404(CommentsModel, id=comment_id)
                form = CommentsForm(request.POST, instance=comment_model)

            if form.is_valid():
                form.instance.comment_post = get_object_or_404(PostsModel, id=post_id)

                comment = self.process_and_save(request, form)
                context = {
                    'post': form.instance.comment_post,
                    'comment': comment,
                }

                try:
                    html_content = render_to_string(self.single_comment_template, context)
                except Exception as e:
                    print(f"Error rendering template: {e}")
                    
                self.broadcast_message(request, 'comment', html_content, post_id)


                if comment_id is None:
                    redirect_url = reverse('post_comments', args=[post_id])
                    return redirect(redirect_url)

                response_data = {
                    'status': 'success',
                    'post': comment.post,
                    'images': None,
                }

                if comment.images:
                    response_data['images'] = comment.images
                return JsonResponse(response_data)

            # Return JSON response with validation errors
            return JsonResponse({'status': 'error', 'message': form.errors})

        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
