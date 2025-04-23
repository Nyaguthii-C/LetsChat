from django.urls import path
from .views import MessageCreateView, MessageDeleteView, MessageUpdateView, ConversationListCreateView, ConversationDetailView

urlpatterns = [
    path('messages/send/', MessageCreateView.as_view(), name='message-send'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    path('conversations/all/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
]
