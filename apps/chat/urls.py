from django.urls import path
from .views import MessageCreateView, ConversationListCreateView, ConversationDetailView

urlpatterns = [
    path('messages/send', MessageCreateView.as_view(), name='send-message'),
    path('conversations/all', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
]
