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
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated


def get_tokens_for_user(user, response=None):
    refresh = RefreshToken.for_user(user)

    access_token = str(refresh.access_token)
    refresh_token = str(refresh)    

    # If a response object is passed, set the refresh token in the HttpOnly cookie
    if response is not None:
        response.set_cookie(
            'refresh_token',  # Cookie name
            refresh_token,  # Value of the refresh token
            httponly=True,  # Prevent access from JavaScript
            secure=False,  # Only set cookie over HTTPS(set fals in development)
            samesite='Lax',  # Ensures the cookie is only sent with same-origin requests('strict' for prod., 'lax'-dev)
            max_age=60 * 60 * 24 * 30,  # Refresh token expires in 30 days
            path='/',
            domain='127.0.0.1',
        )        

    
    # Return the tokens in a dictionary
    return {
        'refresh': refresh_token,
        'access': access_token
    }



class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Get the refresh token from the HttpOnly cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({'error': 'No refresh token provided'}, status=400)

        try:
            # Use the refresh token to generate a new access token
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({'access': new_access_token})
         

        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=400)



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

        user_data = UserSerializer(user).data

        response = JsonResponse({
            'access': tokens['access'],
            'user': user_data,
        })

        # Get the full tokens, including refresh token in HttpOnly cookie
        get_tokens_for_user(user, response=response) # Set refresh token in cookie

        return response



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




class UserListView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all users.",
        operation_summary="Get all users",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of all users.
        """
        return super().get(request, *args, **kwargs)