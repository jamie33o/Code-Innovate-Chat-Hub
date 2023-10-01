
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
         # Check if the user has a related UserProfile
        profile = UserProfile.objects.get(user=instance)
        # Update fields if needed
        profile.save()
    except UserProfile.DoesNotExist:
        # Create a UserProfile if it doesn't exist
        UserProfile.objects.create(user=instance)
