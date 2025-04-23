from django.contrib import admin
from .models import Conversation, Message, Reaction


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'participant_list')
    search_fields = ('participants__email',)
    list_filter = ('created_at',)

    def participant_list(self, obj):
        return ", ".join(user.email for user in obj.participants.all())
    participant_list.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'receiver', 'content_preview', 'timestamp', 'is_read')
    search_fields = ('sender__email', 'receiver__email', 'content')
    list_filter = ('timestamp', 'is_read')

    def content_preview(self, obj):
        return obj.content[:40] + "..." if len(obj.content) > 40 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'emoji')
    search_fields = ('user__email', 'emoji', 'message__content')
    list_filter = ('emoji',)

