import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract channel ID from URL parameters
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        self.room_group_name = f"post_channel_{self.channel_id}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def post_notification(self, event):
        # Send post notification to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'post_content': event['post_content'],
            'post_creator': event['post_creator'],
        }))

   
      