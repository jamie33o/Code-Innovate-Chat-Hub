from django.shortcuts import render

def view_channels(request):
    """ A view that renders the bag contents page """

    return render(request, 'channels/channels.html')
