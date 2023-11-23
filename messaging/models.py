# models.py
from django.db import models
from django.contrib.auth import get_user_model


user = get_user_model()

class ImageModel(models.Model):
    """
    Model for storing images.

    Attributes:
    - image: ImageField for uploading images.

    """
    image = models.ImageField(upload_to='images/')

class EmojiModel(models.Model):
    """
    Model for storing emojis.

    Attributes:
    - emoji_colon_name: Text field for storing the colon representation of the emoji.
    - users_who_incremented: Many-to-Many relationship with users who incremented the emoji.

    Methods:
    - get_incremented_users: Returns the users who incremented the emoji.

    """
    emoji_colon_name = models.TextField(unique=False)
    incremented_by = models.ManyToManyField(user, related_name='%(class)s_incremented_by', blank=True)

    def get_incremented_users(self):
        """
        - get_incremented_users: Returns the users who incremented the emoji.

        """
        return self.users_who_incremented.all()

class Conversation(models.Model):
    participants = models.ManyToManyField(user)

    def delete(self, *args, **kwargs):
        # Delete all messages related to this conversation
        self.messages.all().delete()
        super(Conversation, self).delete(*args, **kwargs)

class Message(models.Model):
    sender = models.ForeignKey(user, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(user, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    images = models.TextField(blank=True, default="")
    emojis = models.ManyToManyField(EmojiModel, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return f"{self.sender} to {self.receiver} - {self.timestamp}"
    


class UnreadMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
