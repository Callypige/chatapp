import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "room_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Retrieve messages from Websocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = data["username"]
        room = data["room"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
                "room": room,
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        room = event["room"]

        # Send message to Websocket
        await self.send(
            text_data=json.dumps(
                {"message": message, "username": username, "room": room}
            )
        )
