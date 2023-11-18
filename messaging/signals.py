from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UnreadMessage, Message

@receiver(post_save, sender=Message)
def create_unread_message(sender, instance, created, **kwargs):
    if created:
        # Create an UnreadMessage instance for the receiver
        UnreadMessage.objects.create(message=instance, user=instance.receiver)
