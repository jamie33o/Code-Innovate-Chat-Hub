import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from .models import ChannelModel,ChannelPosts
from .forms import ChannelPostForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def home_view(request, channel_id=0):
    channels = ChannelModel.objects.all()

    if request.method == 'POST':
        form = handle_form_submission(request, channel_id)

    last_viewed_channel_id = request.user.userprofile.last_viewed_channel_id

    if last_viewed_channel_id and channel_id == 0:
        channel_id = last_viewed_channel_id

    if channel_id > 0:
        channel = get_object_or_404(ChannelModel, id=channel_id)    
        posts = ChannelPosts.objects.filter(post_channel=channel)

        if channel and request.user in channel.users.all() and channel_id:
            update_last_viewed_channel(request, channel_id)

    form = ChannelPostForm()

    context = {
        'channels': channels,
        'channel': None,
        'posts': None,
        'form': form,
        'channel_users': None  # Include user data
    }
    if channel_id > 0:
        context['channel_users'] = channel.users.all()
        context['channel']  = channel
        context['posts']  = posts

    return render(request, 'channels/home.html', context)


def handle_form_submission(request, channel_id):
    form = ChannelPostForm(request.POST)
    if form.is_valid():
        form.instance.post_channel = get_object_or_404(ChannelModel, id=channel_id)
        post = process_and_save_post(request, form, channel_id)
        broadcast_post_notification(request, post, channel_id)
        redirect_url = reverse('channel_posts', args=[channel_id])
        return redirect(redirect_url)
    return form


def process_and_save_post(request, form, channel_id):
    post = form.save(commit=False)
    allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img', 'ol', 'li', 'div', 'span', 'a']
    allowed_attributes = {'*': ['style', 'src', 'href']}
    post.post = bleach.clean(post.post, tags=allowed_tags, attributes=allowed_attributes)
    post.created_by = request.user
    post.post_channel_id = channel_id
    post.save()
    return post


def broadcast_post_notification(request, post, channel_id):
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


def update_last_viewed_channel(request, channel_id):
    last_viewed_url = channel_id
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.last_viewed_url = last_viewed_url
    user_profile.save()


def add_user_to_channel(request, channel_id, user_id):
    """
    This function adds a user to a channel by adding there 
    user object to the channelmodel class: users.

    Parameters:
        request: object provides important information about the incoming request.
        channel_id (int): The channel id the user is being added to
        user_id (int): The id of the user being added

    Returns:
        json object: JsonResponse message success or error
    """

    try:
        # Get the channel and user objects
        channel = get_object_or_404(ChannelModel,id=channel_id)
        user = get_object_or_404(get_user_model(), id=user_id)


        # Add the user to the channel
        channel.users.add(user)

        # Return a JSON response for success
        return JsonResponse({'success': f'{user.username} added to channel'})
    except Exception:
        # Return a JSON response for channel not add user
        return JsonResponse({'error': f'Could not add {user.username}'})
