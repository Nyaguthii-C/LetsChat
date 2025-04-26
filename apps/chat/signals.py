from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.chat.models import Message, Reaction
from apps.notifications.models import Notification
from apps.notifications.utils import notify_user

@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='new_message'
        )
        notify_user(
            instance.receiver.id,
            "new_message",
            {
                "message_id": instance.id,
                "sender_id": instance.sender.id,
                "content": instance.content,
                "timestamp": str(instance.created_at),
            }
        )
        print('new messagenotification incoming')

@receiver(post_save, sender=Reaction)
def handle_reaction(sender, instance, created, **kwargs):
    if created or instance.emoji:
        Notification.objects.create(
            user=instance.message.receiver,
            message=instance.message,
            notification_type="reaction"
        )
        notify_user(
            instance.message.receiver.id,
            "reaction",
            {
                "message_id": instance.message.id,
                "emoji": instance.emoji,
            }
        )
        print('reaction notification incoming')
    
