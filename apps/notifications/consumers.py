from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def typing(self, event):
        await self.send_json(event)

    async def reaction(self, event):
        await self.send_json(event)

    async def read(self, event):
        await self.send_json(event)

    async def new_message(self, event):
        await self.send_json(event)
