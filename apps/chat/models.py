from django.db import models
from django.conf import settings
from apps.users.models import CustomUser

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {', '.join(user.email for user in self.participants.all())}"

    def has_participants(self, user1, user2):
        return self.participants.filter(id=user1.id).exists() and self.participants.filter(id=user2.id).exists()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    class Meta:
        ordering = ['timestamp']

