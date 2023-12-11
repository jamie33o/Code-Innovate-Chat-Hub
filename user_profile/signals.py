"""
Module for handling signals related to user profiles.

This module defines signal handlers that are triggered when certain events occur
in the User model or UserProfile model.

Signal Handlers:
    - create_profile: Creates a UserProfile when a new User is created.
    - save_profile: Saves a UserProfile when a User is saved.
    - update_user_username: Updates a User's username when the associated UserProfile is updated.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

# pylint: disable=no-member
# pylint: disable=unused-argument

@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    """
    Signal handler for creating a UserProfile when a new User is created.

    Args:
        sender: The sender of the signal.
        instance: The User instance being saved.
        created: A boolean indicating if the User instance is newly created.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created:
        UserProfile.objects.create(user=instance, username=instance.username)

@receiver(post_save, sender=get_user_model())
def save_profile(sender, instance, **kwargs):
    """
    Signal handler for saving a UserProfile when a User is saved.

    Args:
        sender: The sender of the signal.
        instance: The User instance being saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.username = instance.username
        profile.save()

@receiver(post_save, sender=UserProfile)
def update_user_username(sender, instance, **kwargs):
    """
    Signal handler for updating a User's username when the associated UserProfile is updated.

    Args:
        sender: The sender of the signal.
        instance: The UserProfile instance being saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if not hasattr(instance, '_update_user_username'):
        if instance.username and instance.user.username != instance.username:
            instance.user.username = instance.username
            #  While it's generally a good practice to avoid using protected members,
            # in this case, it's a deliberate choice to handle a specific situation.
            # pylint: disable=W0212
            instance.user._update_user_username = True  # Mark to avoid recursion
            instance.user.save()
