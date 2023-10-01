# urls.py

from django.urls import path
from .views import UserProfileView, EditUserProfileView

urlpatterns = [
    path('', UserProfileView.as_view(), name='user_profile'),
    path('edit_user_profile/', EditUserProfileView.as_view(), name='edit_user_profile'),
]
