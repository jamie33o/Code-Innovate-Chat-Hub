"""
    AppConfig for the 'group_chat' Django app.
"""
from django.apps import AppConfig

class ChannelsConfig(AppConfig):
    """
    Channels AppConfig for the 'group_chat' Django app.

    Attributes:
    - default_auto_field: A string representing the name of the default auto field for models.
    - name: A string representing the name of the app.

    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'group_chat'
