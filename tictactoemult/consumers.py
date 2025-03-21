import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

# Consumer for matchmaking
class matchmakingConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)("matchmaking", self.channel_name)
        self.accept()

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            "matchmaking",
            {
                "type": "matchmaking.message",
                "text": text_data,
            },
        )

    def matchmaking_message(self, event):
        self.send(text_data=event["text"])

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("matchmaking", self.channel_name)

# Consumer for matches
class matchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the room_name from the URL kwargs
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"match_{self.room_name}"

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            # Log error if something goes wrong
            print(f"Error in connect: {e}")

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        await self.channel_layer.group_discard(
            self.room_group_name,  # Group name
            self.channel_name      # Channel name
        )

    async def receive(self, text_data):
        # Handle receiving a message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'match_message',
                'message': message
            }
        )

    # This method is called when a message is sent to the group
    async def match_message(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))