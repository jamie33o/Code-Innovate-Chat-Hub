from django.shortcuts import render,get_object_or_404,redirect
from .models import ChannelModel,ChannelPosts
from .forms import ChannelPostForm
from django.urls import reverse


def view_channels(request):
    """ A view that renders the channels  page """

    channels = ChannelModel.objects.all()

    context = {
        'channels': channels,
    }

    return render(request, 'channels/channels.html', context)



def channel_posts(request, channel_id):
    """ A view that renders the posts contents page for a specific channel """
    
    # Get the specific channel or return a 404 if it doesn't exist
    channel = get_object_or_404(ChannelModel, id=channel_id)

    if request.method == 'POST':
        form = ChannelPostForm(request.POST)
        if form.is_valid():
            # Add the channel information to the post (you can change this logic)
            form.instance.post_channel = channel
            
            post = form.save(commit=False)
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
        'form': form
    }

    return render(request, 'channels/posts.html', context)

