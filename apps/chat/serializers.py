from rest_framework import serializers
from .models import Conversation, Message
from apps.users.models import CustomUser

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at']
        read_only_fields = ['id', 'created_at']



class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(
        slug_field='email',
        read_only=True
    )

    receiver = serializers.SlugRelatedField(
        slug_field='email',
        read_only=True
    )

    conversation = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'receiver', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp', 'sender']



# show a list of messages inside the conversation detail view
class ConversationDetailSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=CustomUser.objects.all()
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']
