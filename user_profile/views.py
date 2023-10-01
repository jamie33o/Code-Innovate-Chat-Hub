from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import UserProfile
from .forms import UserProfileForm

@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    template_name = 'user_profile/user_profile.html'

    def get(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        return render(request, self.template_name, {'user_profile': user_profile})

@method_decorator(login_required, name='dispatch')
class EditUserProfileView(View):
    template_name = 'user_profile/edit_user_profile.html'
    def get(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        form = UserProfileForm(instance=user_profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # Redirect to the user profile page
        return render(request, self.template_name, {'form': form})

