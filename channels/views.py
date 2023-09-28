import bleach
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import ChannelModel,ChannelPosts
from .forms import ChannelPostForm
from django.http import JsonResponse






def view_channels(request):
    """ A view that renders the channels page  with a list of channels"""

    channels = ChannelModel.objects.all()

    context = {
        'channels': channels,
    }

    return render(request, 'channels/channels.html', context)



def channel_posts(request, channel_id):
    """
    A view that renders the posts contents page for a specific channel

    Parameters:
        request: object provides important information about the incoming request.
        channel_id (int): The channel id the user is being added to

    Returns:
        request: object provides important information about the response
        html: channels/posts.html
        context: extra variables in a dictionary

    """
    # Get the specific channel or return a 404 if it doesn't exist
    channel = get_object_or_404(ChannelModel, id=channel_id)

    if request.method == 'POST':
        form = ChannelPostForm(request.POST)
        
        if form.is_valid():
            # Add the channel information to the post
            form.instance.post_channel = channel
            post = form.save(commit=False)
            allowed_tags = ['b', 'i', 'u', 'p', 'br', 'img','ol','li','div','span','a']
            allowed_attributes = {'*': ['style','src','href']}

            # Clean and sanitize the HTML content
            post.post = bleach.clean(post.post, tags=allowed_tags, attributes=allowed_attributes)
            print(post.post)

            post.created_by = request.user
            post.post_channel_id = channel_id
            post.save()
            redirect_url = reverse('channel_posts', args=[channel_id])
            return redirect(redirect_url)
    else:
        form = ChannelPostForm()

    # Filter posts by the selected channel
    posts = ChannelPosts.objects.filter(post_channel=channel)

    context = {
        'channel': channel,
        'posts': posts,
        'form': form,
        'channel_users': channel.users.all(),  # Include user data
    }

    return render(request, 'channels/posts.html', context)




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
        user = get_object_or_404(User,id=user_id)

        # Add the user to the channel
        channel.users.add(user)

        # Return a JSON response for success
        return JsonResponse({'success': f'{user.username} added to channel'})
    except Exception:
        # Return a JSON response for channel not add user
        return JsonResponse({'error': f'Could not add {user.username}'})
