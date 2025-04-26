from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id, event_type, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": event_type,
            **payload,
        }
    )
