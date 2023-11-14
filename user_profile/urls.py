# urls.py

from django.urls import path
from .views import UserProfileView, update_profile_image, update_status

urlpatterns = [
    path('', UserProfileView.as_view(), name='user_profile'),
    path('update_profile_image/', update_profile_image, name='update_profile_image'),
    path('update_status/', update_status, name='update_status'),
]

