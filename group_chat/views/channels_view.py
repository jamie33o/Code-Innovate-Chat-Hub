from django.utils.decorators import method_decorator
from django.views import View
from group_chat.models import ChannelModel, ChannelLastViewedModel
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse


@method_decorator(login_required, name='dispatch')
class ChannelsView(View):
    template_name = 'channels/home.html'

    def get(self, request, *args, **kwargs):
        channels = ChannelModel.objects.all()
        last_viewed_channel_id = request.user.userprofile.last_viewed_channel_id
          # Create an empty dictionary to store user_status for each channel
        user_statuses = {}

        # Iterate over channels to get user_status for each
        for channel in channels:
            if request.user in channel.users.all():
                user_status, created = ChannelLastViewedModel.objects.get_or_create(
                    user=request.user,
                    channel=channel
                )
                user_statuses[channel.id] = user_status.last_visit

        context = {
            'channels': channels,
            'last_viewed_channel_id': last_viewed_channel_id,
            'user_statuses': user_statuses,  
        }

        return render(request, self.template_name, context)
    

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