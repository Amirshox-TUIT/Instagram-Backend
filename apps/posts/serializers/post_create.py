from rest_framework import serializers
from apps.posts.models import Post
from apps.users.serializers.profile import UserSerializer

class CreatePostSerializer(serializers.ModelSerializer):
    """Post yaratish uchun serializer"""
    caption = serializers.CharField(required=False, allow_blank=True)
    image = serializers.FileField(required=True)

    class Meta:
        model = Post
        fields = ['caption', 'image']