from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'is_seen', 'created_at')
    list_filter = ('notification_type', 'is_seen', 'created_at')
    search_fields = ('user__email', 'message__content')
    date_hierarchy = 'created_at'
