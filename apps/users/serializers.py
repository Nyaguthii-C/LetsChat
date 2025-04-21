from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'profile_photo']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_photo = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'profile_photo']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            profile_photo=validated_data.get('profile_photo')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_photo = serializers.ImageField(required=False)
    email = serializers.EmailField(read_only=True) # do not update/change user email

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password', 'profile_photo']

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            raise serializers.ValidationError("Changing email is not allowed.")
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))  # hash password
        return super().update(instance, validated_data)
