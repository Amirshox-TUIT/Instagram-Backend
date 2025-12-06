from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    recipient_username = serializers.CharField(write_only=True, required=False)
    recipient = serializers.ReadOnlyField(source='recipient.username')
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'recipient',
            'recipient_username',
            'content',
            'created_at',
            'is_read',
            'sender_username',
            'file',
            'file_url',
            'file_name',
            'file_type'
        ]
        read_only_fields = ['id', 'sender', 'created_at']

    def validate_recipient_username(self, value):
        if value and not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Recipient user not found")
        return value

    def validate(self, attrs):
        content = attrs.get('content', '')
        file = attrs.get('file')

        if not self.instance:
            recipient_username = attrs.get('recipient_username')
            if not recipient_username:
                raise serializers.ValidationError({
                    "recipient_username": "Recipient username is required"
                })

            if not content and not file:
                raise serializers.ValidationError({
                    "content": "Content or file is required"
                })

        return attrs

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            import os
            return os.path.basename(obj.file.name)
        return None

    def get_file_type(self, obj):
        if not obj.file:
            return None

        file_name = obj.file.name.lower()

        if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
            return 'image'
        elif file_name.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            return 'video'
        elif file_name.endswith(('.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls')):
            return 'document'
        else:
            return 'file'


class ChatListSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    profile_picture = serializers.SerializerMethodField()
    last_message = serializers.CharField(allow_null=True)
    last_message_time = serializers.DateTimeField(allow_null=True)
    unread_count = serializers.IntegerField()
    is_online = serializers.BooleanField(default=False)

    def get_profile_picture(self, obj):
        if obj.get('profile_picture'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj['profile_picture'])
            return obj['profile_picture']
        return None

