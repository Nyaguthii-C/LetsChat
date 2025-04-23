from django.urls import path
from .views import MessageCreateView, MessageDeleteView, MessageUpdateView, ConversationListCreateView, ConversationDetailView

urlpatterns = [
    path('messages/send/', MessageCreateView.as_view(), name='send-message'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message-update'),
    path('conversations/all/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
]
