from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Message, Conversation, Reaction
from .serializers import MessageSerializer, ConversationDetailSerializer, ConversationSerializer, ReactionSerializer
from .services import GetStreamService
from apps.users.models import CustomUser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.db import transaction
from apps.notifications.utils import notify_user
from uuid import uuid4
import uuid



class MessageCreateView(generics.CreateAPIView):
    """
    post:
    Send a message from the logged-in user to another user using GetStream.io.

    Requires:
    - receiver: ID of the user to send the message to
    - content: The message text

    This will create a new channel if one does not exist or send a message to the existing one.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Send a message to another user using GetStream.io.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["receiver", "content"],
            properties={
                "receiver": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the receiver user"),
                "content": openapi.Schema(type=openapi.TYPE_STRING, description="Message content"),
            },
        ),
        responses={
            200: openapi.Response(description="Message sent successfully."),
            400: "Bad Request",
            401: "Unauthorized",
            404: "Receiver not found",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)



    def perform_create(self, serializer):
        sender = self.request.user
        receiver_id = self.request.data.get('receiver')
        content = self.request.data.get('content')

        if not receiver_id or not content:
            raise ValidationError({"receiver": "Receiver is required.", "content": "Content is required."})

        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            raise NotFound(f"Receiver with ID {receiver_id} not found.")

        conversation = Conversation.objects.filter(participants=sender)\
                                        .filter(participants=receiver)\
                                        .first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.set([sender, receiver])

        stream_service = GetStreamService()
        channel = stream_service.create_or_get_channel(sender, receiver)

        stream_service.send_message(channel, sender, receiver, content)

        self.message_instance = serializer.save(
            sender=sender,
            receiver=receiver,
            content=content,
            conversation=conversation,
            is_read=False
        )


        message_data = MessageSerializer(self.message_instance).data

        notify_user(
            user_id=receiver.id,
            notification_type='new_message',
            data=message_data  # This is now safe
        )


    # for HTTP response
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call perform_create to handle message creation logic
        self.perform_create(serializer)

        message_data = MessageSerializer(self.message_instance).data
        return Response({
            "success": True,
            "message": "Message sent successfully.",
            "data": message_data
        }, status=status.HTTP_201_CREATED)



class MessageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update the content of a message. Only the sender can update.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content"],
            properties={
                "content": openapi.Schema(type=openapi.TYPE_STRING, description="Updated message content"),
            },
        ),
        responses={
            200: openapi.Response("Message updated successfully.", MessageSerializer),
            400: "Content is required.",
            403: "You are not authorized to update this message.",
            404: "Message not found.",
        }
    )    

    def patch(self, request, *args, **kwargs):
        try:
            message = Message.objects.get(id=kwargs['pk'])
        except Message.DoesNotExist:
            raise NotFound("Message not found.")

        if message.sender != request.user:
            raise PermissionDenied("You cannot update this message.")

        content = request.data.get('content')
        if not content:
            raise ValidationError("Content is required.")

        message.content = content
        message.save()

        message_data = MessageSerializer(message).data
        return Response({
            "success": True,
            "message": "Message updated successfully.",
            "data": message_data
        }, status=status.HTTP_200_OK)



class MessageDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a message by ID. Only the sender or staff can delete.",
        responses={
            204: "Message deleted successfully.",
            403: "You are not authorized to delete this message.",
            404: "Message not found.",
        }
    )    

    def delete(self, request, *args, **kwargs):
        try:
            message = Message.objects.get(id=kwargs['pk'])
        except Message.DoesNotExist:
            raise NotFound("Message not found.")

        if message.sender != request.user and not request.user.is_staff:
            raise PermissionDenied("You are not authorized to delete this message.")

        message.delete()

        return Response({
            "success": True,
            "message": "Message deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)



class MarkMessageReadView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Mark a message as read",
        responses={
            200: "Mark a message as read.",
            403: "You cannot mark this message as read.",
            404: "Message not found.",
        }
    ) 

    def patch(self, request, *args, **kwargs):
        try:
            message = Message.objects.get(id=kwargs['pk'])
        except Message.DoesNotExist:
            raise NotFound("Message not found.")

        if message.receiver != request.user:
            raise PermissionDenied("You cannot mark this message as read.")

        message.is_read = True
        message.save()

        return Response({
            "success": True,
            "message": "Message marked as read."}, status=status.HTTP_200_OK)




class AddReactionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add or update a reaction (emoji) to a message. Only one reaction per user per message.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["emoji"],
            properties={
                "emoji": openapi.Schema(type=openapi.TYPE_STRING, description="Emoji reaction (e.g. 👍, ❤️)"),
            },
        ),
        responses={
            200: openapi.Response(description="Reaction added or updated successfully."),
            400: "Emoji is required.",
            401: "Authentication required.",
            404: "Message not found.",
        }
    )
    def post(self, request, message_id):
        emoji = request.data.get('emoji')
        user = request.user

        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise NotFound("Message not found.")

        if not emoji:
            raise ValidationError("Emoji is required.")

        reaction, created = Reaction.objects.get_or_create(
            message=message, user=user, defaults={'emoji': emoji}
        )
        notify_user(
            user_id=message.sender.id,
            notification_type='reaction',
            data={
                'id': str(uuid.uuid4()),
                'message_id': message.id,
                'user_id': user.id,
                'reaction_type': emoji
            }
        )

        if not created:
            reaction.emoji = emoji
            reaction.save()

        return Response({"success": True, "message": "Reaction added successfully."})



class RemoveReactionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Remove the current user's reaction from a message. Idempotent: returns 204 even if no reaction exists.",
        responses={
            204: "Reaction removed or no reaction found.",
            401: "Authentication required.",
            404: "Message not found.",
        }
    )
    def post(self, request, message_id):
        user = request.user

        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise NotFound("Message not found.")

        # find user's reaction
        reaction = Reaction.objects.filter(message=message, user=user).first()

        if reaction:
            reaction.delete()

        return Response(status=204)



class ConversationListCreateView(generics.ListCreateAPIView):
    """
    get:
    Retrieve all conversations where the current user is a participant.

    post:
    Create a new conversation and automatically add the current user as a participant.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    @swagger_auto_schema(
        operation_description="List all conversations for the current user.",
        responses={200: ConversationSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new conversation. The current user is automatically added as a participant.",
        request_body=ConversationSerializer,
        responses={
            201: openapi.Response("Conversation created successfully", ConversationSerializer),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        participants = serializer.validated_data.get('participants', [])
        if self.request.user not in participants:
            participants.append(self.request.user)
        conversation = serializer.save()
        conversation.participants.add(*participants)



class ConversationDetailView(generics.RetrieveAPIView):
    """
    get:
    Retrieve the details of a single conversation that the authenticated user is a participant of.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # return Conversation.objects.filter(participants=self.request.user)
        queryset = Conversation.objects.filter(participants=self.request.user)
        filter_params = self.request.query_params

        # Filter by read status
        is_read = filter_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(messages__is_read=is_read)

        # Filter by message content (search)
        search = filter_params.get('search')
        if search:
            queryset = queryset.filter(messages__content__icontains=search)

        # Filter by date range
        created_at_start = filter_params.get('created_at_start')
        created_at_end = filter_params.get('created_at_end')
        if created_at_start and created_at_end:
            queryset = queryset.filter(messages__created_at__range=[created_at_start, created_at_end])

        return queryset        

    @swagger_auto_schema(
        operation_description="Retrieve a specific conversation by ID. The current user must be a participant.",
        responses={
            200: openapi.Response("Conversation details retrieved", ConversationDetailSerializer),
            404: "Conversation not found or access denied"
        }
    )
    def get(self, request, *args, **kwargs):       
        return super().get(request, *args, **kwargs)  


def get_conversation_between(user1, user2):
    conversations = Conversation.objects.filter(participants=user1).filter(participants=user2)
    return conversations.first()  # or .last() depending on need



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_with(request, user_email):
    try:
        other_user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    conversation = get_conversation_between(request.user, other_user)

    if conversation:
        return Response({'id': conversation.id})
    return Response({'id': None})




from django.dispatch import receiver
from django.db.models.signals import post_save
import traceback
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_signals(request):
    """
    Debug endpoint to test if signals are working properly
    """
    try:
        # Get the first other user to use as receiver
        receiver_user = CustomUser.objects.exclude(id=request.user.id).first()
        if not receiver_user:
            return Response({"error": "No other user found to use as receiver"}, status=400)
        
        # Find or create a conversation between sender and receiver
        conversation = Conversation.objects.filter(participants=request.user)\
                                           .filter(participants=receiver_user)\
                                           .first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.set([request.user, receiver_user])
        
        # Log current signal connections
        from django.db.models import signals
        for r in signals.post_save.receivers:
            print(f"  - {r}")
        
        # Dynamically register test signal handler
        @receiver(post_save, sender=Message)
        def test_signal_handler(sender, instance, created, **kwargs):
            
            # Create notification if not exists
            if created:
                Notification.objects.get_or_create(
                    user=instance.receiver,
                    message=instance,
                    defaults={
                        'is_read': False,
                        'notification_type': 'message'
                    }
                )

        
        # Create a test message
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver_user,
            conversation=conversation,
            content="Test message for debugging signals",
            is_read=False
        )
        
        
        # Check if notifications were created
        notifications = Notification.objects.filter(message=message).count()
        
        return Response({
            "success": True,
            "message_id": message.id,
            "conversation_id": conversation.id,
            "receiver_id": receiver_user.id,
            "notifications_count": notifications,
            "message": "See server console for signal debug output"
        })
    
    except Exception as e:
        print(f"Error in debug_signals: {str(e)}")
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)