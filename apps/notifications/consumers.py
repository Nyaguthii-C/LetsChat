from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from apps.notifications.models import Notification
from apps.notifications.utils import mark_notifications_as_seen


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection
        - Add user to their notification group
        - Send initial unread notification count
        """
        user = self.scope["user"]
        if user.is_authenticated:
            self.user_id = user.id
            self.group_name = f"user_{user.id}"
            
            # Add to user's notification group
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            
            # Send unread notifications and count
            unread_notifications = await self.get_unread_notifications(user.id)
            await self.send_json({
                "type": "initial_notifications",
                "unread_count": len(unread_notifications),
                "notifications": unread_notifications
            })
        else:
            await self.close()

    async def disconnect(self, close_code):
        """
        Remove user from their notification group on disconnect
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        """
        Handle incoming WebSocket messages
        """
        action = content.get("action")
        
        if action == "mark_seen":
            notification_ids = content.get("notification_ids", [])
            await self.mark_notifications_seen(notification_ids)

    # Channel layer event handlers
    async def new_message(self, event):
        await self.send_json(event["data"])
    
    async def reaction(self, event):
        await self.send_json(event["data"])

    async def reaction_added(self, event):
        """
        Specific handler for reaction added events
        """
        await self.send_json(event["data"])
    
    async def reaction_removed(self, event):
        """
        Specific handler for reaction removed events
        """
        await self.send_json(event["data"])



    # Handler for 'notifications_seen' message type
    async def notifications_seen(self, event):
        notification_ids = event["data"].get("notification_ids", [])
        
        # update frontend UI (removing or marking notifications as seen)
        await self.send_json({
            "type": "notifications_seen", 
            "notification_ids": notification_ids
        })


    
    @database_sync_to_async
    def get_unread_notifications(self, user_id):
        notifications = Notification.objects.filter(
            user_id=user_id, 
            is_seen=False
        ).order_by('-created_at')[:10]

        return [
            {
                "id": str(notif.id),
                "type": notif.notification_type,
                "userName": (
                    notif.reaction.user.full_name if notif.notification_type == 'reaction' and notif.reaction
                    else notif.message.sender.full_name if notif.message else "System"
                ),
                "timeAgo": self.format_time_ago(notif.created_at),
                "unread": True,
                "content": notif.message.content if notif.message else None,
                "messageId": notif.message.id if notif.message else None,
                "reactor_data": {
                    "full_name": notif.reaction.user.full_name,
                } if notif.notification_type == 'reaction' and notif.reaction else None,
            } for notif in notifications
        ]


    @database_sync_to_async
    def mark_notifications_seen(self, notification_ids):
        """
        Mark specific notifications as seen
        """        
        # Convert string IDs to integers
        notification_ids = [int(id) for id in notification_ids]
        
        # Mark notifications as seen
        mark_notifications_as_seen(self.user_id, notification_ids)
        
        return True

    def format_time_ago(self, timestamp):
        """
        Format timestamp to human-readable time ago
        """
        from django.utils.timesince import timesince
        return timesince(timestamp) + " ago"