"""
views for the channels
"""
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.http import Http404
from group_chat.models import ChannelModel, ChannelLastViewedModel

# pylint: disable=no-member

@method_decorator(login_required, name='dispatch')
class ChannelsView(View):
    """
    View class for displaying a list of channels.
    """

    template_name = 'group_chat/home.html'

    def get(self, request):
        """
        Handle GET requests to display the list of channels.

        Returns:
            HttpResponse: Rendered template with channel information.
        """

        channels = ChannelModel.objects.all()
        last_viewed_channel_id = request.user.userprofile.last_viewed_channel_id

        # Create an empty dictionary to store user_status for each channel
        user_statuses = {}

        # Iterate over channels to get user_status for each
        for channel in channels:
            try:
                if request.user in channel.users.all():
                    user_status, _ = ChannelLastViewedModel.objects.get_or_create(
                        user=request.user,
                        channel=channel,
                    )
                    user_statuses[channel.id] = user_status.last_visit
            except ChannelLastViewedModel.DoesNotExist:
                # Handle the case where ChannelLastViewedModel
                # does not exist for the user and channel
                user_statuses[channel.id] = None

        context = {
            'channels': channels,
            'last_viewed_channel_id': last_viewed_channel_id,
            'user_statuses': user_statuses,
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class AddUserToChannelView(View):
    """
    View class for adding a user to a channel.
    """

    def post(self, request, channel_id, user_id):
        # NOTE: The request parameter is not used in this method, but it is kept for consistency.

        """
        Handle POST requests to add a user to a channel.

        Args:
            channel_id (int): The ID of the channel.
            user_id (int): The ID of the user.

        Returns:
            JsonResponse: JSON response indicating the status of the operation.
        """

        try:
            channel = get_object_or_404(ChannelModel, id=channel_id)
            user = get_object_or_404(get_user_model(), id=user_id)

            # Add the user to the channel
            channel.users.add(user)

            context = {
                'status': 'success',
                'message': f'{user.username} has been added to {channel.name}'
            }

            return JsonResponse(context)
        except Http404:
            # Handle Http404 exceptions for the get_object_or_404 calls
            return JsonResponse({
                'status': 'Error',
                'message': 'Object not found'
            })
        except Exception as e:
            # If an exception occurs, handle it and provide an appropriate response
            return JsonResponse({
                'status': 'Error',
                'message': f'Could not add {user.username} to {channel.name}, Error: {str(e)}'
            })
