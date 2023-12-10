"""
Views for handling user profile.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from group_chat.models import SavedPost, PostsModel
from .models import UserProfile
from .forms import ProfileImageForm, EditProfileForm, StatusForm
from django.core.exceptions import PermissionDenied

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

@require_POST
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
            return JsonResponse({'success': 'image',
                                 'message': image.profile_picture.url}, status=200)
        return JsonResponse({'status': 'error',
                             'message': 'Error updating profile picture',
                             'errors': form.errors}, status=400)
    form = ProfileImageForm(instance=request.user.userprofile)
    return '403.html'

@require_POST
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
            return JsonResponse({'status': 'success', 'message': status.status }, status=200)
        return JsonResponse({'status': 'error',
                             'message': f'Error updating status: {form.errors}'}, status=400)
    form = StatusForm(instance=request.user.userprofile)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=500)

@require_POST
@login_required
def remove_saved_post(request, post_id):
    """
    Remove a saved post for the currently logged-in user.

    Args:
        post_id (int): The ID of the post to be removed from saved posts.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        # Retrieve the post instance
        post = get_object_or_404(PostsModel, id=post_id)

        # Check if the post is saved by the user
        saved_posts = SavedPost.objects.filter(user=request.user, post=post)

        if saved_posts.exists():
            # If the post is saved, remove it
            saved_posts.delete()
            return JsonResponse({'status': 'Success', 'message': 'Post removed'}, status=200)
  
        # If the post is not saved, return an error
        return JsonResponse({'status': 'Error', 'message': 'Post does not exist'}, status=400)
    except Exception:
        # Return an error for non-POST requests
        return JsonResponse({'status': 'Error', 'message': 'Invalid request method'}, status=500)


def get_all_users_profiles(request):
    """
    view for retrieving all users profiles and creating a list 
    of username, id and profile_picture url for search bar in 
    the header section of site
    """
    if request.is_ajax():
        try:
            user_profiles = UserProfile.objects.all().values('username', 'id', 'profile_picture')
            return JsonResponse(list(user_profiles), safe=False)
        except Exception:
            return JsonResponse({'status': 'Error', 'message': 'Invalid request method'}, status=500)
    raise PermissionDenied



@require_POST
@login_required  # Ensure that only authenticated users can access this endpoint
def delete_user_account(request):
    """
    Deletes the user account of the authenticated user.

    Parameters:
    - request: The HTTP request object.

    Returns:
    A JSON response indicating the status of the operation.
    """
    try:
        # Retrieve the authenticated user
        user = get_object_or_404(get_user_model(), id=request.user.id)

        # Delete the user account
        user.delete()

        return JsonResponse({'status': 'Success', 'message': 'Account Deleted'}, status=200)

    except Exception as e:
        # Handle exceptions and return an appropriate error response
        return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)