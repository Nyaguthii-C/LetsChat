from django.db import models
from django.conf import settings
from apps.chat.models import Message, Reaction

class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ("new_message", "New Message"),
        ("reaction", "Reaction"),
        ("read", "Read"),
        ("typing", "Typing"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # to be notified
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
