from rest_framework import serializers
from ..models import Comment, Post, User


class CommentUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    userPicture = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'username', 'userPicture', 'text', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_userPicture(self, obj):
        if hasattr(obj.user, 'profile_picture') and obj.user.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
            return obj.user.profile_picture.url
        return None


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['post', 'text']
