from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationDetailSerializer, ConversationSerializer
from .services import GetStreamService
from apps.users.models import CustomUser
from rest_framework import status

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
        receiver = CustomUser.objects.get(id=self.request.data['receiver'])

        # Validate that content and receiver are provided
        if not receiver_id or not content:
            raise ValidationError("Receiver and content are required.")

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

        content = self.request.data['content']
        stream_service.send_message(channel, sender, receiver, content)

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            conversation=conversation,
            is_read=False
        )

        self.message_instance = message

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
        return Conversation.objects.filter(participants=self.request.user)

    @swagger_auto_schema(
        operation_description="Retrieve a specific conversation by ID. The current user must be a participant.",
        responses={
            200: openapi.Response("Conversation details retrieved", ConversationDetailSerializer),
            404: "Conversation not found or access denied"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
