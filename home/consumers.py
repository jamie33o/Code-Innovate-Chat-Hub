import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.get_room_group_name()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    def get_room_group_name(self):
        raise NotImplementedError("Subclasses must implement this method")

    async def post_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'post_notification',
            'message': event['message'],
            'post_content': event['post_content'],
            'post_creator': event['post_creator'],
        }))

    async def comment_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'comment_notification',
            'message': event['message'],
            'comment_content': event['comment_content'],
            'comment_creator': event['comment_creator'],
        }))
class PostConsumer(BaseConsumer):
    def get_room_group_name(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        return f"post_channel_{self.channel_id}"

class CommentConsumer(BaseConsumer):
    def get_room_group_name(self):
        self.post_id = self.scope["url_route"]["kwargs"]["post_id"]
        return f"comment_post{self.post_id}"

   
      