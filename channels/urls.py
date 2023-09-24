from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_channels, name='view_channels')
]
