from rest_framework import serializers
from .models import Notification
from apps.chat.serializers import MessageSerializer
from django.contrib.auth import get_user_model
from apps.chat.models import Reaction

User = get_user_model()

class UserMinimalSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_photo']
    
    def get_profile_photo(self, obj):
        if obj.profile_photo:
            return obj.profile_photo
        return None
    
    def get_full_name(self, obj):
        return obj.full_name

class NotificationSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True)
    related_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'notification_type', 'created_at', 'is_seen', 'related_user']
    
    def get_related_user(self, obj):
        """
        Get the user related to this notification (e.g., message sender or reaction creator)
        """
        related_user = None
        
        if obj.notification_type == 'new_message' and obj.message:
            related_user = obj.message.sender
        elif obj.notification_type == 'reaction' and obj.message:
            # Find the user who created the reaction
            try:
                reaction = Reaction.objects.filter(message=obj.message).latest('created_at')
                related_user = reaction.user
            except Reaction.DoesNotExist:
                pass
        
        if related_user:
            return UserMinimalSerializer(related_user).data
        return None