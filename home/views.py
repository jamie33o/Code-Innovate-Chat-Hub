import bleach
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from .models import ChannelModel,ChannelPosts
from .forms import ChannelPostForm




@login_required
def home_view(request, channel_id=0):
    """ A view that renders the channels page  with a list of channels"""

    channels = ChannelModel.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    form = ChannelPostForm(request.POST)

    # last_viewed_channel_id = user_profile.last_viewed_channel_id
    last_viewed_channel_id = request.user.userprofile.last_viewed_channel_id

    if last_viewed_channel_id and channel_id == 0:
        channel_id = last_viewed_channel_id
    
    channel = None
    # Get the specific channel or return a 404 if it doesn't exist
    if channel_id > 0:
        channel = get_object_or_404(ChannelModel, id=channel_id)
   
    if request.method == 'POST':
        if form.is_valid():
            # Add the channel information to the post
            form.instance.post_channel = channel
            post = form.save(commit=False)
            allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img','ol','li','div','span','a']
            allowed_attributes = {'*': ['style','src','href']}

            # Clean and sanitize the HTML content
            post.post = bleach.clean(post.post, tags=allowed_tags, attributes=allowed_attributes)

            post.created_by = request.user
            post.post_channel_id = channel_id
            post.save()
            redirect_url = reverse('channel_posts', args=[channel_id])
            return redirect(redirect_url)
    if channel:
        if request.user in channel.users.all() and channel_id:
            last_viewed_url = channel_id
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.last_viewed_url = last_viewed_url
            user_profile.save()

    form = ChannelPostForm()

    # Filter posts by the selected channel
    posts = ChannelPosts.objects.filter(post_channel=channel)

    context = {
        'channels': channels,
        'channel': channel,
        'posts': posts,
        'form': form,
        'channel_users': None  # Include user data
    }
    if channel:
        context['channel_users'] = channel.users.all()

    return render(request, 'channels/home.html', context)



# def channel_posts(request, channel_id, small_screen):
#     """
#     A view that renders the posts contents page for a specific channel

#     Parameters:
#         request: object provides important information about the incoming request.
#         channel_id (int): The channel id the user is being added to

#     Returns:
#         request: object provides important information about the response
#         html: channels/posts.html
#         context: extra variables in a dictionary

#     """

#     # Get the specific channel or return a 404 if it doesn't exist
#     channel = get_object_or_404(ChannelModel, id=channel_id)
#     form = ChannelPostForm(request.POST)

#     if request.method == 'POST':
#         if form.is_valid():
#             # Add the channel information to the post
#             form.instance.post_channel = channel
#             post = form.save(commit=False)
#             allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img','ol','li','div','span','a']
#             allowed_attributes = {'*': ['style','src','href']}

#             # Clean and sanitize the HTML content
#             post.post = bleach.clean(post.post, tags=allowed_tags, attributes=allowed_attributes)

#             post.created_by = request.user
#             post.post_channel_id = channel_id
#             post.save()
#             redirect_url = reverse('channel_posts', args=[channel_id,small_screen])
#             return redirect(redirect_url)

#     if request.user in channel.users.all():
#         last_viewed_url = reverse('channel_posts', args=[channel_id, 'False'])
#         user_profile = UserProfile.objects.get(user=request.user)
#         user_profile.last_viewed_url = last_viewed_url
#         user_profile.save()

#     form = ChannelPostForm()

#     # Filter posts by the selected channel
#     posts = ChannelPosts.objects.filter(post_channel=channel)

#     context = {
#         'channel': channel,
#         'posts': posts,
#         'form': form,
#         'channel_users': channel.users.all(),  # Include user data
#     }

#     return render(request, 'channels/posts.html', context)


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
