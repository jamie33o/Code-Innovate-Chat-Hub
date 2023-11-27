"""
Views for handling user profile.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from group_chat.models import SavedPost, PostsModel
from .models import UserProfile
from .forms import ProfileImageForm, EditProfileForm, StatusForm

# pylint: disable=no-member
@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    """
    View for displaying and updating user profiles.
    """
    template_name = 'user_profile/user_profile.html'

    def get(self, request):
        """
        Handle GET requests to display the user profile.

        Returns:
            HttpResponse: The rendered user profile page.
        """
        user_profile = get_object_or_404(UserProfile, user=request.user)
        saved_posts = SavedPost.objects.filter(user=request.user)
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
    

@method_decorator(login_required, name='dispatch')
class ViewUserProfile(View):
    """
    View for displaying and updating user profiles.
    """
    template_name = 'user_profile/view-user-profile.html'

    def get(self, request, user_id):
        """
        Handle GET requests to display the user profile.

        Returns:
            HttpResponse: The rendered user profile page.
        """
        user_profile = get_object_or_404(UserProfile, id=user_id)

        context = {
            'user_profile': user_profile,
        }
        return render(request, self.template_name, context)
    


    def post(self, request):
        """
        Handle POST requests to update the user profile.

        Returns:
            HttpResponse: The rendered user profile page or a redirect.
        """
        edit_profile_form = EditProfileForm(request.POST, instance=request.user.userprofile)
        if edit_profile_form.is_valid():
            edit_profile_form.save()
            return redirect('user_profile')  # Redirect to the user profile page

        return render(request, self.template_name, {'Edit_profile_form': edit_profile_form})

@login_required
def update_profile_image(request):
    """
    Update the profile picture of the currently logged-in user.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            image = form.save()
            return JsonResponse({'success': 'image', 'message': image.profile_picture.url})
        return JsonResponse({'success': False, 'message': 'Error updating profile picture', 
                             'errors': form.errors})
    form = ProfileImageForm(instance=request.user.userprofile)
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_status(request):
    """
    View for updating the user's status.

    Args:
    - request: HTTP request object.

    Returns:
    - JsonResponse: JSON response indicating success or failure.
    """
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            status = form.save()
            return JsonResponse({'status': 'success', 'message': status.status })
        return JsonResponse({'success': False, 
                             'message': 'Error updating status', 
                             'errors': form.errors})
    form = StatusForm(instance=request.user.userprofile)
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def remove_saved_post(request, post_id):
    """
    Remove a saved post for the currently logged-in user.

    Args:
        post_id (int): The ID of the post to be removed from saved posts.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    if request.method == 'POST':
        # Retrieve the post instance
        post = get_object_or_404(PostsModel, id=post_id)

        # Check if the post is saved by the user
        saved_posts = SavedPost.objects.filter(user=request.user, post=post)

        if saved_posts.exists():
            # If the post is saved, remove it
            saved_posts.delete()
            return JsonResponse({'status': 'Success', 'message': 'Post removed'})
       
        # If the post is not saved, return an error
        return JsonResponse({'status': 'Error', 'message': 'Post is not saved'})

    # Return an error for non-POST requests
    return JsonResponse({'status': 'Error', 'message': 'Invalid request method'})


def get_all_users_profiles(request):
    user_profiles = UserProfile.objects.all().values('username', 'id', 'profile_picture')
    return JsonResponse(list(user_profiles), safe=False)
