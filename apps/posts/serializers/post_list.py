from rest_framework import serializers
from apps.posts.models import Post
from apps.users.serializers.profile import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'caption',
            'image',
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
        return obj.comment.count()


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comment = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    image = serializers.FileField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'caption', 'image', 'likes', 'comment', 'created_at']
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