from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from apps.notifications.models import Notification
from django.contrib.auth import get_user_model

def notify_user(user_id, notification_type, data):
    channel_layer = get_channel_layer()
    
    # Add type field to data for frontend processing
    data['type'] = notification_type
    
    # For message notifications, include sender data
    if notification_type == 'new_message' and 'sender_id' in data:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            sender = User.objects.get(id=data['sender_id'])
            data['sender_data'] = {
                'id': sender.id,
                'name': sender.full_name,
                'profile_photo': sender.profile_photo.url if sender.profile_photo else None,
            }
        except User.DoesNotExist:
            pass
    
    # For reaction notifications, include user data (who reacted)
    if notification_type == 'reaction' and 'user_id' in data:
        User = get_user_model()
        try:
            user = User.objects.get(id=data['user_id'])
            data['reactor_data'] = {
                'id': user.id,
                'name': user.full_name,
                'profile_photo': user.profile_photo if user.profile_photo else None,
            }
        except User.DoesNotExist:
            pass
    
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": notification_type,
            "data": data
        }
    )

def mark_notifications_as_seen(user_id, notification_ids=None):
    """
    Mark notifications as seen for a user
    If notification_ids is provided, only mark those notifications
    Otherwise mark all unseen notifications for the user
    """
 
    notifications = Notification.objects.filter(user_id=user_id, is_seen=False)
    if notification_ids:
        notifications = notifications.filter(id__in=notification_ids)
    
    # Update all matching notifications
    count = notifications.update(is_seen=True)
    
    # Notify client about seen status update
    if count > 0:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "notifications_seen",
                "data": {
                    "type": "notifications_seen",
                    "notification_ids": list(notifications.values_list('id', flat=True))
                }
            }
        )
    
    return count