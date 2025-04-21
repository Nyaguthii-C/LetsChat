from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UpdateUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(generics.CreateAPIView):
    """
    post:
    Register a new user with email, full_name, password, and optional profile photo.
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=RegisterSerializer,
        manual_parameters=[
            openapi.Parameter(
                'profile_photo', 
                openapi.IN_FORM, 
                description="Profile Photo", 
                type=openapi.TYPE_FILE
            )
        ],        
        responses={
            201: openapi.Response('User created successfully', RegisterSerializer),
            400: "Bad request"
        }
    )
    def create(self, request, *args, **kwargs):
        # DRF handles validation, saving, and error handling
        response = super().create(request, *args, **kwargs)
        
        return Response({
            "message": "User account created successfully.",
            "data": response.data
        }, status=response.status_code)



class LoginView(APIView):
    """
    post:
    Login with email and password to receive JWT tokens (access & refresh).
    """
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        request_body=LoginSerializer,
        operation_description="Authenticate user and return JWT tokens.",
        responses={
            200: openapi.Response("JWT tokens returned"),
            400: "Invalid credentials"
        }
    )    

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = get_tokens_for_user(user)
        return Response(tokens)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateUserSerializer
        return UserSerializer    

    @swagger_auto_schema(operation_description="Get current user's profile.")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Update current user's profile.")
    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "User profile updated successfully.",
            "data": response.data
        }, status=response.status_code)

    @swagger_auto_schema(operation_description="Delete current user account.")
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({
            "message": "User account deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        return self.request.user

