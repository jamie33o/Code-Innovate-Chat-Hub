import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from group_chat.models import ChannelModel, PostsModel, ChannelLastViewedModel, CommentsModel
from group_chat.forms import PostsForm, CommentsForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



class BaseChatView(View):
    template_name = None  # Set this in the subclass
    def process_and_save(self, request, form):
        instance = form.save(commit=False)
        url_list = request.POST.getlist('urls[]')
        instance.images = ",".join(url_list)
        # allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
        # allowed_attributes = {'*': ['style', 'src', 'href']}
        # instance.post = bleach.clean(instance.post, tags=allowed_tags, attributes=allowed_attributes)
        instance.created_by = request.user
        instance.save()

        return instance

    def broadcast_message(self, request, message_type, message_content, instance_id):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{message_type}{instance_id}",
            {
                'type': f'{message_type}_notification',
                'message': f'New {message_type} added!',
                f'{message_type}_content': message_content,
                f'{message_type}_creator': request.user.username,
            }
        )


@method_decorator(login_required, name='dispatch')
class PostsView(BaseChatView):
    template_name = 'group_chat/posts.html'
    paginated_template ='group_chat/paginated-posts.html'
    posts_per_page = 10

    def get_channel(self, channel_id):
        return get_object_or_404(ChannelModel, id=channel_id)

    def get_posts(self, channel):
        return PostsModel.objects.filter(post_channel=channel).order_by('created_date')

    def get_paginated_posts(self, posts, page):
        paginator = Paginator(posts, self.posts_per_page)
        total_pages = paginator.num_pages

        page = total_pages if not page else total_pages - page 
      
        try:
            # Start from the last page and go backward
            paginated_posts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):           
             # If the page is not an integer, show the last page
            paginated_posts = paginator.page(total_pages)


        prev_page_number = paginated_posts.previous_page_number() if paginated_posts.has_previous() else None

        return paginated_posts, prev_page_number

    def update_user_status(self, request, channel):
        user_status, created = ChannelLastViewedModel.objects.get_or_create(
            user=request.user,
            channel=channel
        )
        user_status.last_visit = timezone.now()
        user_status.save()

    def get(self, request, channel_id, *args, **kwargs):
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
            #self.broadcast_message(request, 'post_channel_', post.post, channel_id)

            # Process and save images
            if post_id is None:
                redirect_url = reverse('channel_posts', args=[channel_id])

                return redirect(redirect_url)
            
            # if its an edited post post_id will not be none
            response_data = {
                'status': 'success',
                'post': post.post,
                'images': None,
            }

            if post.images:
                response_data['images'] = post.images
            return JsonResponse(response_data)
        
        return render(request, self.template_name, {'form': form})

    def update_last_viewed_channel(self, request, channel_id):
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.last_viewed_channel_id = channel_id
        user_profile.save()
    
    def users_that_commented(self, paginated_posts):
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
    template_name = 'group_chat/comments.html'

    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(PostsModel, id=post_id)
        comments = CommentsModel.objects.filter(comment_post=post)

        form = CommentsForm()

        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }

        return render(request, self.template_name, context)

    def post(self, request, post_id, comment_id=None, *args, **kwargs):

        if comment_id == None:
            form = CommentsForm(request.POST)
        else:
            post = get_object_or_404(CommentsModel, id=comment_id)
            form = CommentsForm(request.POST, instance=post)

        if form.is_valid():
            form.instance.comment_post = get_object_or_404(PostsModel, id=post_id)

            comment = self.process_and_save(request, form)
            #self.broadcast_comment(request, comment.post,comment_post, post_id)
            if comment_id is None:
                redirect_url = reverse('post_comments', args=[post_id])
                return redirect(redirect_url)
            else:
                response_data = {
                    'status': 'success',
                    'post': comment.post,
                    'images': None,
                }

                if comment.images:
                    response_data['images'] = comment.images
                return JsonResponse(response_data)

        else:
            print(form.errors)
            # return response with error message


           