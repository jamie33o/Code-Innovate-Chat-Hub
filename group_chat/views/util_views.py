from django.http import JsonResponse
from group_chat.models import PostsModel, CommentsModel, ImageModel,EmojiModel
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.shortcuts import get_object_or_404
from django.apps import apps



@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadView(View):
    def post(self, request, *args, **kwargs):
        if request.FILES.get('file'):
            # Assuming 'file' is the name of your file input field
            image_file = request.FILES['file']

            # Create a new Image instance
            new_image = ImageModel.objects.create(image=image_file)

            # Return the URL or other information
            return JsonResponse({'url': new_image.image.url})

        return JsonResponse({'error': 'Invalid request'}, status=400)
        

@method_decorator(csrf_exempt, name='dispatch')
class AddOrUpdateEmojiView(View):
    def post(self, request, id, *args, **kwargs):
        user = request.user
        emoji_colon_name = request.POST.get('emoji_colon_name')

        if 'post_emoji' in request.path:

            # Get the PostsModel
            channel_post = PostsModel.objects.get(pk=id)

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
            post_comment = CommentsModel.objects.get(pk=id)

            # Add the emoji to the emojis field
            post_comment.emojis.add(emoji_instance)   
    
        return JsonResponse({'status': 'success'}) 



class GenericObjectDeleteView(DeleteView):

    def get_object(self, queryset=None):
        # Get the model class based on the URL parameter
        model_name = self.kwargs['model']
        model = apps.get_model(app_label='group_chat', model_name=model_name)

        # Get the object to be deleted
        obj_pk = self.kwargs['pk']
        obj = get_object_or_404(model, pk=obj_pk)

        return obj
    
    def delete(self, request, *args, **kwargs):
        # Get the object to be deleted
        obj = self.get_object()

        # Delete the object
        obj.delete()
        # Override the delete method to return a JSON response
        response_data = {'status': 'success'}
        return JsonResponse(response_data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.kwargs['model']
        return context
