from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.chat.models import Message, Reaction
from apps.notifications.models import Notification
from apps.notifications.utils import notify_user
import logging

logger = logging.getLogger(__name__)

# Define signal handlers
def handle_new_message(sender, instance, created, **kwargs):
    print(f"Signal handle_new_message fired. Message ID: {instance.id}, Created: {created}")
    logger.info(f"Signal handle_new_message fired. Message ID: {instance.id}, Created: {created}")
    
    if created:
        try:
            # Create database notification
            notification = Notification.objects.create(
                user=instance.receiver,
                message=instance,
                notification_type='new_message'
            )
            
            print(f"Notification created: {notification.id} for message {instance.id}")
            logger.info(f"Notification created: {notification.id} for message {instance.id}")
            
            # Send real-time notification
            notify_user(
                instance.receiver.id,
                "new_message",
                {
                    "notification_id": notification.id,
                    "message_id": instance.id,
                    "sender_id": instance.sender.id,
                    "content": instance.content,
                    "timestamp": str(instance.timestamp),
                    "conversation_id": instance.conversation.id if instance.conversation else None
                }
            )
        except Exception as e:
            print(f"Error in handle_new_message signal: {str(e)}")
            logger.error(f"Error in handle_new_message signal: {str(e)}")

def handle_reaction(sender, instance, created, **kwargs):
    print(f"Signal handle_reaction fired. Reaction ID: {instance.id}, Created: {created}")
    logger.info(f"Signal handle_reaction fired. Reaction ID: {instance.id}, Created: {created}")
    
    # Only notify if it's a new reaction or the emoji changed
    if created or getattr(instance, '_loaded_values', {}).get('emoji') != instance.emoji:
        try:
            # Create database notification
            notification = Notification.objects.create(
                user=instance.message.sender if instance.message.sender != instance.user else instance.message.receiver,
                message=instance.message,
                notification_type="reaction"
            )
            
            print(f"Reaction notification created: {notification.id}")
            logger.info(f"Reaction notification created: {notification.id}")
            
            # Send real-time notification
            notify_user(
                notification.user.id,  # Send to the appropriate user (not the reactor)
                "reaction",
                {
                    "notification_id": notification.id,
                    "message_id": instance.message.id,
                    "user_id": instance.user.id,  # Who reacted
                    "emoji": instance.emoji,
                    "timestamp": str(instance.message.timestamp)
                }
            )
        except Exception as e:
            print(f"Error in handle_reaction signal: {str(e)}")
            logger.error(f"Error in handle_reaction signal: {str(e)}")

# Explicitly connect the signals
# This will be called when this module is imported
print("Connecting signal handlers for Message and Reaction models...")
post_save.connect(handle_new_message, sender=Message)
post_save.connect(handle_reaction, sender=Reaction)
print("Signal handlers connected successfully")