from django.shortcuts import render, redirect
from .forms import ProfileImageForm

def upload_profile_image(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Replace 'profile' with the name of your profile view
    else:
        form = ProfileImageForm(instance=request.user)
    
    return render(request, 'upload_profile_image.html', {'form': form})
