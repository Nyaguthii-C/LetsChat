from django.urls import path
from .views import NotificationListView, MarkNotificationsSeenView

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/mark-seen/', MarkNotificationsSeenView.as_view(), name='mark-notifications-seen'),
]