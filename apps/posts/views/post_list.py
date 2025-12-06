from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView

from apps.posts.models import Post
from apps.posts.serializers.post_list import PostSerializer, PostDetailSerializer
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse
from rest_framework import generics, permissions, status

User = get_user_model()

class TimelineAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    serializer_class = PostSerializer

    def get_queryset(self):
        following_users = self.request.user.following.all()
        posts = Post.objects.filter(
            author__in=following_users
        ) | Post.objects.filter(author=self.request.user)
        posts = posts.distinct().order_by('-created_at')
        return posts

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(message_key='POST_FETCHED', data=serializer.data, status_code=status.HTTP_200_OK)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                request=request,
                data=serializer.data
            )
        except Post.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Post"}
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        try:
            instance = self.get_object()
        except Post.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Post"}
            )

        if instance.author != request.user:
            return CustomResponse.forbidden(
                message_key="PERMISSION_DENIED",
                request=request,
                context={"action": "update this post"}
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            return CustomResponse.validation_error(
                errors=serializer.errors,
                request=request
            )

        if 'caption' in serializer.validated_data:
            instance.caption = serializer.validated_data['caption']

        instance.save()

        response = self.get_serializer(instance)

        return CustomResponse.success(
            request=request,
            data=response.data
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Post.DoesNotExist:
            return CustomResponse.not_found(
                message_key="NOT_FOUND",
                request=request,
                context={"resource": "Post"}
            )

        if instance.author != request.user:
            return CustomResponse.forbidden(
                message_key="PERMISSION_DENIED",
                request=request,
                context={"action": "delete this post"}
            )

        instance.delete()

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            request=request,
            data={"detail": "Post deleted successfully"},
            status_code=status.HTTP_204_NO_CONTENT
        )

class PostLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        post.save()

        return CustomResponse.success(data={"likes_count": post.likes.count()}, status=status.HTTP_200_OK)


class UserArticleListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user).select_related('author').prefetch_related('likes')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )