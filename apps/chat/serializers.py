from rest_framework import serializers
from .models import Conversation, Message
from apps.users.models import CustomUser
from rest_framework.pagination import PageNumberPagination



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



class MessagePagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100



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
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        messages = data.get('messages', [])
        paginator = MessagePagination()
        result_page = paginator.paginate_queryset(messages, self.context['request'])
        return paginator.get_paginated_response(result_page)