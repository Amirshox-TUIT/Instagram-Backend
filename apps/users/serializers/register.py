from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException


User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=128)
    email = serializers.EmailField()

    def validate_username(self, username):
        if len(username.strip()) == 0:
            raise serializers.ValidationError("Username cannot be empty")
        return username

    def validate_email(self, email):
        if len(email.strip()) == 0:
            raise serializers.ValidationError("Email cannot be empty")
        return email

    def validate_password(self, password):
        if len(password.strip()) < 8 or password.isdigit() or password.isalpha():
            raise CustomException(message_key='VALIDATION_ERROR', context={'password': password})
        return password


