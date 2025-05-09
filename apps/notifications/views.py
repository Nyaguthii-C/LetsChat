from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Notification
from .serializers import NotificationSerializer
from .utils import mark_notifications_as_seen

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="List all notifications for the authenticated user",
        manual_parameters=[
            openapi.Parameter(
                'is_seen',
                openapi.IN_QUERY,
                description="Filter by seen status",
                type=openapi.TYPE_BOOLEAN,
                required=False
            )
        ],
        responses={
            200: NotificationSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        is_seen = request.query_params.get('is_seen')
        queryset = self.get_queryset()
        
        if is_seen is not None:
            is_seen = is_seen.lower() == 'true'
            queryset = queryset.filter(is_seen=is_seen)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MarkNotificationsSeenView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Mark notifications as seen",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'notification_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="List of notification IDs to mark as seen. If not provided, all unseen notifications will be marked."
                )
            },
            required=[]
        ),
        responses={
            200: openapi.Response(
                description="Notifications marked as seen",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of notifications marked as seen")
                    }
                )
            ),
            401: "Unauthorized"
        }
    )
    def post(self, request):
        notification_ids = request.data.get('notification_ids')
        
        count = mark_notifications_as_seen(request.user.id, notification_ids)
        
        return Response({
            'success': True,
            'count': count
        })

