import json
from channels.generic.websocket import WebsocketConsumer
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