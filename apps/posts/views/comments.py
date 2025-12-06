from rest_framework import status, generics
from rest_framework.generics import DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from ..models import Comment, Post
from ..serializers.comments import CommentSerializer, CommentCreateSerializer
from ...shared.exceptions.custom_exceptions import CustomException
from ...shared.utils.custom_response import CustomResponse


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            post_id = request.data.get('articleId') or request.data.get('post')
            comment_text = request.data.get('description') or request.data.get('text')

            if not post_id:
                return CustomResponse.error(
                    message_key="VALIDATION_ERROR",
                    errors={"error": "Post ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not comment_text:
                return CustomResponse.error(
                    message_key="VALIDATION_ERROR",
                    errors={"error": "Comment text is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            post = get_object_or_404(Post, id=post_id)
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                text=comment_text
            )
            serializer = CommentSerializer(comment, context={'request': request})

            return CustomResponse.success(data=serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PostCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).select_related('user', 'post').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return CustomResponse.success(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateSerializer

    def get_object(self):
        comment = get_object_or_404(Comment, id=self.kwargs.get('comment_id'))
        if comment.user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        return comment
