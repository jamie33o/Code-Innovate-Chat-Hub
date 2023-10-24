import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from .models import ChannelModel, ChannelPosts, PostComments, Image,EmojiModel
from .forms import ChannelPostForm, PostCommentsForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt




@method_decorator(login_required, name='dispatch')
class HomeView(View):
    template_name = 'channels/home.html'

    def get(self, request, *args, **kwargs):
        channels = ChannelModel.objects.all()
        last_viewed_channel_id = request.user.userprofile.last_viewed_channel_id

        context = {
            'channels': channels,
            'last_viewed_channel_id': last_viewed_channel_id,
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

        # Add messages
        messages.success(request, f'Success: {request.user.username} added to channel')
       
        messages.error(request, f'Error: Could not add {request.user.username} to channel')
        messages.error(request, f'Error: Please enter text', extra_tags='summernote-error')

        context = {
            'channel': channel,
            'posts': posts,
            'form': form,
            'channel_users': channel.users.all()
        }
        return render(request, self.template_name, context)

    def post(self, request, channel_id, *args, **kwargs):
        form = ChannelPostForm(request.POST)
        if form.is_valid():
            form.instance.post_channel = get_object_or_404(ChannelModel, id=channel_id)
            post = self.process_and_save(request, form)                
            #self.broadcast_post(request, post, channel_id)
            # Process and save images
            redirect_url = reverse('channel_posts', args=[channel_id])
            return redirect(redirect_url)
        else:
            print(form.errors)
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
            #self.broadcast_comment(request, comment, post_id)

            redirect_url = reverse('post_comments', args=[post_id])
            return redirect(redirect_url)
        else:
            print(form.errors)
            # return response with error message

    def process_and_save(self, request, form):
        comment = form.save(commit=False)
        # allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
        # allowed_attributes = {'*': ['style', 'src', 'href','class']}
        # allowed_styles = ['display', 'width', 'height', 'background', 'background-size']

        # comment.post = bleach.clean(comment.post, tags=allowed_tags, attributes=allowed_attributes, styles=allowed_styles)
        comment.created_by = request.user
        comment.save()

        return comment
    def broadcast_comment(self, request, comment, post_id):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"comment_post{post_id}",
            {
                'type': 'comment_notification',
                'message': 'New post added!',
                'comment_content': comment.post,
                'comment_creator': request.user.username,
            }
        )


@method_decorator(login_required, name='dispatch')
class AddUserToChannelView(View):

    def post(self, request, channel_id, user_id, *args, **kwargs):
        try:
            channel = get_object_or_404(ChannelModel, id=channel_id)
            user = get_object_or_404(get_user_model(), id=user_id)

            # Add the user to the channel
            channel.users.add(user)

            return JsonResponse({'status': 'success'})
        except Exception:
            return JsonResponse({'status': 'error'})


@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadView(View):
    def post(self, request, *args, **kwargs):
        if request.FILES.get('file'):
            # Assuming 'file' is the name of your file input field
            image_file = request.FILES['file']

            # Create a new Image instance
            new_image = Image.objects.create(image=image_file)

            # Return the URL or other information
            return JsonResponse({'url': new_image.image.url})

        return JsonResponse({'error': 'Invalid request'}, status=400)
    

@method_decorator(csrf_exempt, name='dispatch')
class AddOrUpdateEmojiView(View):
    def post(self, request, id, *args, **kwargs):
        user = request.user
        emoji_colon_name = request.POST.get('emoji_colon_name')

        if 'post_emoji' in request.path:

            # Get the ChannelPosts
            channel_post = ChannelPosts.objects.get(pk=id)

                        # If it exists, increment the count and add the user
            post_emoji_instance, created = channel_post.emojis.get_or_create(
                emoji_colon_name=emoji_colon_name,
                defaults={'emoji_colon_name': emoji_colon_name}
            )

            if created:
                # If a new instance is created, add the user
                post_emoji_instance.users_who_incremented.add(request.user)
                return JsonResponse({'status': 'added'})

            # Check if the EmojiModel exists in channel_post
            else:
                if request.user in post_emoji_instance.users_who_incremented.all():
                    post_emoji_instance.users_who_incremented.remove(request.user)
                    # Check if there are no more users and remove the instance if true
                    if post_emoji_instance.users_who_incremented.count() == 0:
                        channel_post.emojis.remove(post_emoji_instance)                                                                                                                                                                                                                                                         
                        return JsonResponse({'status': 'removed'})
                    return JsonResponse({'status': 'decremented'})
                else:
                    # If it exists, increment the count and add the user
                    post_emoji_instance.users_who_incremented.add(request.user)
                    return JsonResponse({'status': 'incremented'})
                
        else:
            emoji_instance, created = EmojiModel.objects.get_or_create(
            created_by=user,
            emoji_colon_name=emoji_colon_name
            )

           
            # Get the PostComment
            post_comment = PostComments.objects.get(pk=id)

            # Add the emoji to the emojis field
            post_comment.emojis.add(emoji_instance)   
    
        return JsonResponse({'status': 'success'}) 
    
  