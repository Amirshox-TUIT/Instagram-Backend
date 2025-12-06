import os

from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.serializers.profile import UserSerializer

from apps.reels.models import Reel, ReelsComment


class ReelListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = [
            'id',
            'author',
            'content',
            'file',
            'likes_count',
            'is_liked',
            'comments_count',
            'created_at',
            'updated_at'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request:
            return request.user in obj.likes.all()
        return False

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_file(self, file):
        ALLOWED_VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.avi')
        file_name = file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        if file_extension not in ALLOWED_VIDEO_EXTENSIONS:
            raise CustomException(message_key="VALIDATION_ERROR")

        return file


class ReelDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comment = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    image = serializers.FileField(read_only=True)

    class Meta:
        model = Reel
        fields = ['id', 'author', 'content', 'image', 'likes', 'comment', 'created_at']
        read_only_fields = ['id', 'author', 'likes', 'comment', 'created_at']

    def get_comment(self, obj):
        return obj.comment.count()

    def get_author_profile_picture(self, obj):
        if obj.author.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.author.profile_picture.url)
            return obj.author.profile_picture.url
        return None


class CommentListCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    userPicture = serializers.SerializerMethodField()

    class Meta:
        model = ReelsComment
        fields = ['id', 'reel', 'user', 'username', 'userPicture', 'text', 'created_at']
        read_only_fields = ['id', 'reel', 'user', 'created_at']

    def get_userPicture(self, obj):
        if hasattr(obj.user, 'profile_picture') and obj.user.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
            return obj.user.profile_picture.url
        return None


class CommentRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReelsComment
        fields = ['text']

    def validate_text(self, text):
        if text.strip() == "":
            raise CustomException(message_key="VALIDATION_ERROR")
        return text
