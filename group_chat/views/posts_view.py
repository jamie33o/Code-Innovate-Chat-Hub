import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from group_chat.models import ChannelModel, PostsModel, ChannelLastViewedModel
from group_chat.forms import PostsForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@method_decorator(login_required, name='dispatch')
class PostsView(View):
    template_name = 'channels/posts.html'
    paginated_template ='channels/paginated-posts.html'
    posts_per_page = 10

    def get(self, request, channel_id, *args, **kwargs):
        channel = get_object_or_404(ChannelModel, id=channel_id)
        
        posts = PostsModel.objects.filter(post_channel=channel).order_by('created_date')
        # Pagination
        paginator = Paginator(posts, self.posts_per_page)
        page = request.GET.get('page')


        try:
            paginated_posts = paginator.page(page)
        except PageNotAnInteger:
            paginated_posts = paginator.page(1)
        except EmptyPage:
            paginated_posts = paginator.page(paginator.num_pages)


          # Create a list to store information about users who commented for each post
        post_comments_users = {}

        for post in posts:
           # Get the comments for the current post
            comments = post.comments_created.all()

            # Extract user IDs of users who have commented on the post
            commented_users_ids = comments.values_list('created_by', flat=True)

            # Retrieve additional information about the users
            commented_users_info = get_user_model().objects.filter(id__in=commented_users_ids)
            # Create a dictionary with user information for each post
            post_comments_users[post.id] = {
                'post': paginated_posts,
                'commented_users': commented_users_info,
            }

        if request.user in channel.users.all():
            self.update_last_viewed_channel(request, channel_id)

        form = PostsForm()

        # Update the user's last visit status for the channel
        user_status, created = ChannelLastViewedModel.objects.get_or_create(
            user=request.user,
            channel=channel
        )

        user_status.last_visit = timezone.now()
        user_status.save()


        # Add messages
        messages.success(request, f'Success: {request.user.username} added to channel')
       
        messages.error(request, f'Error: Could not add {request.user.username} to channel')
        messages.error(request, f'Error: Please enter text', extra_tags='summernote-error')


        next_page_number = paginated_posts.next_page_number() if paginated_posts.has_next() else None

        context = {
            'channel': channel,
            'posts': paginated_posts,
            'form': form,
            'channel_users': channel.users.all(),
            'next_page_number': next_page_number,
            'post_comments_users': post_comments_users
        }

        if page:
            return render(request, self.paginated_template, context)

        return render(request, self.template_name, context)

    def post(self, request, channel_id, post_id=None, *args, **kwargs):

         # If post_id is None, it's a new post; otherwise, it's an edit
        if post_id == None:
            form = PostsForm(request.POST)
        else:
            post = get_object_or_404(PostsModel, id=post_id)
            form = PostsForm(request.POST, instance=post)
            

        if form.is_valid():
            form.instance.post_channel = get_object_or_404(ChannelModel, id=channel_id)
            post = self.process_and_save(request, form)                
            #self.broadcast_post(request, post, channel_id)
            # Process and save images
            if post_id is None:
                redirect_url = reverse('channel_posts', args=[channel_id])

                return redirect(redirect_url)
            else:
                response_data = {
                    'status': 'success',
                    'post': post.post,
                    'images': post.images,
                }

                return JsonResponse(response_data)
        else:
            return render(request, self.template_name, {'form': form})

    def process_and_save(self, request, form):
        post = form.save(commit=False)
        url_list = request.POST.getlist('urls[]')
        post.images = ",".join(url_list)
        # allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
        # allowed_attributes = {'*': ['style', 'src', 'href']}
        # post.post = bleach.clean(post.post, tags=allowed_tags, attributes=allowed_attributes)
        post.created_by = request.user
        post.save()

        return post


    def broadcast_post(self, request, post, channel_id):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"post_channel_{channel_id}",
            {
                'type': 'post_notification',
                'message': 'New post added!',
                'post_content': post.post,
                'post_creator': request.user.username,
            }
        )

    def update_last_viewed_channel(self, request, channel_id):
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.last_viewed_channel_id = channel_id
        user_profile.save()
