from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from rest_framework.views import APIView

from .models import Message
from .serializers import MessageSerializer, ChatListSerializer
from django.contrib.auth import get_user_model
from apps.shared.utils.custom_response import CustomResponse

User = get_user_model()


class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        username = self.kwargs.get('username')

        try:
            recipient = User.objects.get(username=username)
        except User.DoesNotExist:
            return Message.objects.none()

        Message.objects.filter(
            sender=recipient,
            recipient=self.request.user,
            is_read=False
        ).update(is_read=True)

        return Message.objects.filter(
            Q(sender=self.request.user, recipient=recipient) |
            Q(sender=recipient, recipient=self.request.user)
        ).order_by('created_at')

    def list(self, request, *args, **kwargs):
        username = self.kwargs.get('username')

        try:
            recipient = User.objects.get(username=username)
        except User.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Recipient user"}
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            request=request,
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.validation_error(
                errors=serializer.errors,
                request=request
            )

        recipient_username = serializer.validated_data.get('recipient_username')
        try:
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            return CustomResponse.not_found(
                request=request,
                context={"resource": "Recipient user"}
            )

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=serializer.validated_data.get('content', ''),
            file=serializer.validated_data.get('file')
        )

        result_serializer = self.get_serializer(message)
        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            request=request,
            data=result_serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class MessageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Message.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Message"}
            )

        serializer = self.get_serializer(instance)

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            request=request,
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
        except Message.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Message"}
            )
        if instance.sender != request.user:
            return CustomResponse.forbidden(
                message_key="PERMISSION_DENIED",
                request=request,
                context={"action": "edit this message"}
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return CustomResponse.validation_error(
                errors=serializer.errors,
                request=request
            )

        if 'content' in serializer.validated_data:
            instance.content = serializer.validated_data['content']
        if 'is_read' in serializer.validated_data:
            instance.is_read = serializer.validated_data['is_read']

        instance.save()

        result_serializer = self.get_serializer(instance)

        return CustomResponse.success(
            request=request,
            data=result_serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Message.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Message"}
            )

        if instance.sender != request.user:
            return CustomResponse.forbidden(
                request=request,
                context={"action": "delete this message"}
            )

        instance.delete()

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            request=request,
            data={"detail": "Message deleted successfully"},
            status_code=status.HTTP_204_NO_CONTENT
        )


class ChatListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            current_user = request.user
            messages = Message.objects.filter(
                Q(sender=current_user) | Q(recipient=current_user)
            )

            if not messages.exists():
                return CustomResponse.success(
                    message_key="SUCCESS_MESSAGE",
                    request=request,
                    data=[]
                )

            chat_users = set()
            for msg in messages:
                other_user = msg.recipient if msg.sender == current_user else msg.sender
                chat_users.add(other_user.id)

            chats = []
            for user_id in chat_users:
                other_user = User.objects.get(id=user_id)
                last_message = Message.objects.filter(
                    Q(sender=current_user, recipient=other_user) |
                    Q(sender=other_user, recipient=current_user)
                ).order_by('-created_at').first()

                unread_count = Message.objects.filter(
                    sender=other_user,
                    recipient=current_user,
                    is_read=False
                ).count()


                chat_data = {
                    'user_id': other_user.id,
                    'username': other_user.username,
                    'profile_picture': other_user.profile_picture.url if other_user.profile_picture else None,
                    'last_message': last_message.content if last_message else None,
                    'last_message_time': last_message.created_at if last_message else None,
                    'unread_count': unread_count,
                    'is_online': False
                }
                chats.append(chat_data)

            chats.sort(key=lambda x: x['last_message_time'] if x['last_message_time'] else '', reverse=True)
            serializer = ChatListSerializer(chats, many=True, context={'request': request})
            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                request=request,
                data=serializer.data
            )

        except Exception as e:
            return CustomResponse.error(
                message_key="SERVER_ERROR",
                request=request,
                errors={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnreadMessagesCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            unread_count = Message.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()

            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                request=request,
                data={"unread_count": unread_count}
            )

        except Exception as e:
            return CustomResponse.error(
                message_key="SERVER_ERROR",
                request=request,
                errors={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )