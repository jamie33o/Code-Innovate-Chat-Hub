from django.urls import path
from . import views

urlpatterns = [
    path('profile_images/', views.upload_profile_image),
   
]