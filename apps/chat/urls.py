from django.urls import path
from .views import ( MessageCreateView, MessageDeleteView, MessageUpdateView, MarkMessageReadView, 
            AddReactionView, RemoveReactionView, ConversationListCreateView, ConversationDetailView
)
from . import views

urlpatterns = [
    path('messages/send/', MessageCreateView.as_view(), name='message-send'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    path('messages/<int:pk>/mark-as-read/', MarkMessageReadView.as_view(), name='message-mark-read'),
    path('messages/<int:message_id>/react/', AddReactionView.as_view(), name='add-reaction'),
    path('messages/<int:message_id>/remove-reaction/', RemoveReactionView.as_view(), name='remove-reaction'),
    path('conversations/all/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/with/<user_email>/', views.get_conversation_with, name='conversation-with-user'),
]
