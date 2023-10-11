
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=get_user_model())
def save_profile(sender, instance, **kwargs):
    try:
        profile = UserProfile.objects.get(user=instance)
        # Update fields if needed
        profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
