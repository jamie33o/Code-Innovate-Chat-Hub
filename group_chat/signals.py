# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from PIL import Image as PILImg
# from django.core.files.storage import default_storage
# from .models import ImageModel

# @receiver(post_save, sender=ImageModel)
# def resize_image(sender, instance, **kwargs):
#     # Check if the instance has an image field and if the image has changed
#     if hasattr(instance, 'image') and instance.image and instance.image.url and kwargs.get('created', False):
#         # Open the image file
#         with default_storage.open(instance.image.name, 'rb') as file:
#             image = PILImg.open(file)

#             # Resize the image
#             resized_image = image.resize((300, 200))

#             # Save the resized image back to the same path
#             with default_storage.open(instance.image.name, 'wb') as resized_file:
#                 resized_image.save(resized_file)

# # Connect the signal
# post_save.connect(resize_image, sender=ImageModel)
