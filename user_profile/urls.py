"""URL patterns for user profile-related views."""

from django.urls import path
from .views import UserProfileView, ViewUserProfile, update_profile_image, update_status

urlpatterns = [
    path('', UserProfileView.as_view(), name='user_profile'),
    path('update_profile_image/', update_profile_image, name='update_profile_image'),
    path('update_status/', update_status, name='update_status'),
    path('view_user_profile/<int:user_id>/', ViewUserProfile.as_view(), name='view_user_profile'),
]

