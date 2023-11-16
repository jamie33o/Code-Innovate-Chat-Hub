from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from group_chat.models import SavedPost
from django.http import JsonResponse
from .forms import ProfileImageForm, EditProfileForm, StatusForm
from .models import UserProfile


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    template_name = 'user_profile/user_profile.html'
  

    def get(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        saved_posts = SavedPost.objects.filter(user=request.user)
        # Retrieve the actual posts
        posts = [saved_post.post for saved_post in saved_posts]

        edit_profile_form = EditProfileForm(instance=user_profile)
        profile_image_form = ProfileImageForm(instance=user_profile)
        status_form = StatusForm(instance=user_profile)

        context = {
            'user_profile': user_profile,
            'Edit_profile_form': edit_profile_form,
            'profile_image_form': profile_image_form,
            'status_form': status_form,
            'posts': posts,
        }
        return render(request, self.template_name, context)
    

    def post(self, request):
        edit_profile_form = EditProfileForm(request.POST, instance=request.user.userprofile)
        if edit_profile_form.is_valid():

            edit_profile_form.save()

            return redirect('user_profile')  # Redirect to the user profile page
        
        return render(request, self.template_name, {'Edit_profile_form': edit_profile_form})
    
@login_required
def update_profile_image(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            image = form.save()
            return JsonResponse({'success': 'image', 'message': image.profile_picture.url})
        return JsonResponse({'success': False, 'message': 'Error updating profile picture', 'errors': form.errors})
    form = ProfileImageForm(instance=request.user.userprofile)
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_status(request):
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            status = form.save()
            return JsonResponse({'status': 'success', 'message': status.status })
        return JsonResponse({'success': False, 'message': 'Error updating status', 'errors': form.errors})
    form = StatusForm(instance=request.user.userprofile)
    return JsonResponse({'success': False, 'message': 'Invalid request'})




