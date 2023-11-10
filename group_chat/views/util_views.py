from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.apps import apps
from group_chat.models import PostsModel, ImageModel, SavedPost



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

        return JsonResponse({'status': 'Error', 'message': 'Image could not be uploaded'})        
    

@method_decorator(csrf_exempt, name='dispatch')
class AddOrUpdateEmojiView(View):
    def post(self, request, instance_id, *args, **kwargs):
        try:
            user = request.user
            emoji_colon_name = request.POST.get('emoji_colon_name')

            # Get the model class based on the URL parameter
            model_name = self.kwargs['model']
            model = apps.get_model(app_label='group_chat', model_name=model_name)

            obj = get_object_or_404(model, pk=instance_id)

            # If it exists, increment the count and add the user
            instance, created = obj.emojis.get_or_create(
                emoji_colon_name=emoji_colon_name,
                defaults={'emoji_colon_name': emoji_colon_name}
            )

            if created:
                # If a new instance is created, add the user
                instance.users_who_incremented.add(request.user)
                return JsonResponse({'status': 'added'})

            # Check if the EmojiModel exists in channel_post
            else:
                if request.user in instance.users_who_incremented.all():
                    instance.users_who_incremented.remove(request.user)
                    # Check if there are no more users and remove the instance if true
                    if instance.users_who_incremented.count() == 0:
                        obj.emojis.remove(instance)
                        return JsonResponse({'status': 'removed'})
                    return JsonResponse({'status': 'decremented'})
                else:
                    # If it exists, increment the count and add the user
                    instance.users_who_incremented.add(request.user)
                    return JsonResponse({'status': 'incremented'})
        except Exception as e:
            # Handle exceptions (e.g., model not found, database error)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



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

        model_name = obj.__class__.__name__
        # Delete the object
        obj.delete()
        # Override the delete method to return a JSON response
        return JsonResponse({'status': 'success', 'message': f'{model_name[:-6] } deleted'})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.kwargs['model']
        return context


class SavePostView(View):
    def post(self, request, post_id):
        post = get_object_or_404(PostsModel, id=post_id)  

        # Check if the post is already saved by the user
        if SavedPost.objects.filter(user=request.user, post=post).exists():
            return JsonResponse({'status': 'Error', 'message': 'Post already saved'})

        # Save the post for the user
        saved_post = SavedPost(user=request.user, post=post)
        saved_post.save()

        return JsonResponse({'status': 'Success', 'message': 'Post saved'})