from rest_framework import serializers
from .models import Conversation, Message, Reaction
from apps.users.models import CustomUser
from rest_framework.pagination import PageNumberPagination



class ReactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Reaction
        fields = ['user', 'emoji']



class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(slug_field='email', read_only=True)
    receiver = serializers.SlugRelatedField(slug_field='email', read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'receiver', 'content', 'reactions', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp', 'sender']



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