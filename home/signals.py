from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image as PILImg  
from django.contrib.auth.models import User 
from .models import Image

@receiver(post_save, sender=Image)
def resize_image(sender, instance, **kwargs):
    # Check if the instance has an image field and if the image has changed
    if hasattr(instance, 'image') and instance.image and instance.image.path and kwargs.get('created', False):
        # Open the image file
        image = PILImg.open(instance.image.path)

        # Resize the image
        resized_image = image.resize((300, 200))

        # Save the resized image back to the same path
        resized_image.save(instance.image.path)

# Connect the signal
post_save.connect(resize_image, sender=Image)