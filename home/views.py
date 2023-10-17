import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from .models import ChannelModel, ChannelPosts, PostComments
from .forms import ChannelPostForm, PostCommentsForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views import View
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    template_name = 'channels/home.html'

    def get(self, request, *args, **kwargs):
        channels = ChannelModel.objects.all()
        last_viewed_channel_id = request.user.userprofile.last_viewed_channel_id

        context = {
            'channels': channels,
            'channel_id': last_viewed_channel_id,
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ChannelPostsView(View):
    template_name = 'channels/posts.html'

    def get(self, request, channel_id, *args, **kwargs):
        channel = get_object_or_404(ChannelModel, id=channel_id)
        posts = ChannelPosts.objects.filter(post_channel=channel)

        if request.user in channel.users.all():
            self.update_last_viewed_channel(request, channel_id)

        form = ChannelPostForm()

        context = {
            'channel': channel,
            'posts': posts,
            'form': form,
            'channel_users': channel.users.all(),
        }

        return render(request, self.template_name, context)

    def post(self, request, channel_id, *args, **kwargs):
        form = ChannelPostForm(request.POST)
        if form.is_valid():
            form.instance.post_channel = get_object_or_404(ChannelModel, id=channel_id)
            post = self.process_and_save(request, form)
            self.broadcast_post_notification(request, post, channel_id)

            redirect_url = reverse('channel_posts', args=[channel_id])
            return redirect(redirect_url)
        else:
            print(form.errors)
            return render(request, self.template_name, {'form': form})

    def process_and_save(self, request, form):
        post = form.save(commit=False)
        allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
        allowed_attributes = {'*': ['style', 'src', 'href']}
        post.post = bleach.clean(post.post, tags=allowed_tags, attributes=allowed_attributes)
        post.created_by = request.user
        post.save()

        return post


    def broadcast_post_notification(self, request, post, channel_id):
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
        last_viewed_url = channel_id
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.last_viewed_url = last_viewed_url
        user_profile.save()



@method_decorator(login_required, name='dispatch')
class PostCommentsView(View):
    template_name = 'channels/comments.html'

    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(ChannelPosts, id=post_id)
        comments = PostComments.objects.filter(comment_post=post)

        form = PostCommentsForm()

        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }

        return render(request, self.template_name, context)

    def post(self, request, post_id, *args, **kwargs):
        form = PostCommentsForm(request.POST)
        if form.is_valid():

            form.instance.comment_post = get_object_or_404(ChannelPosts, id=post_id)

            comment = self.process_and_save(request, form)
            # self.broadcast_post_notification(request, comment, post_id)

            redirect_url = reverse('post_comments', args=[post_id])
            return redirect(redirect_url)
        else:
            print(form.errors)
            # return response with error message

    def process_and_save(self, request, form):
        comment = form.save(commit=False)
        allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
        allowed_attributes = {'*': ['style', 'src', 'href']}
        comment.post = bleach.clean(comment.post, tags=allowed_tags, attributes=allowed_attributes)
        comment.created_by = request.user
        comment.save()

        return comment


@method_decorator(login_required, name='dispatch')
class AddUserToChannelView(View):

    def post(self, request, channel_id, user_id, *args, **kwargs):
        try:
            channel = get_object_or_404(ChannelModel, id=channel_id)
            user = get_object_or_404(get_user_model(), id=user_id)

            # Add the user to the channel
            channel.users.add(user)

            return JsonResponse({'success': f'{user.username} added to channel'})
        except Exception:
            return JsonResponse({'error': f'Could not add user to channel'})
