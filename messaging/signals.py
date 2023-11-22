from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UnreadMessage, Message

@receiver(post_save, sender=Message)
def create_unread_message(sender, instance, created, **kwargs):
     if created:
        # Check if there's already an UnreadMessage for this conversation and receiver
        existing_unread_message = UnreadMessage.objects.filter(
            conversation=instance.conversation,
        ).first()

        if not existing_unread_message:
            # Create an UnreadMessage instance for the receiver
            UnreadMessage.objects.create(
                conversation=instance.conversation,
            )