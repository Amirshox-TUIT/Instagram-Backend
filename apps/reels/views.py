from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.reels.models import Reel, ReelsComment
from apps.reels.serializers import ReelListSerializer, ReelDetailSerializer, CommentListCreateSerializer, \
    CommentRetrieveUpdateDestroySerializer
from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse

User = get_user_model()

class ReelListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = CustomPageNumberPagination
    serializer_class = ReelListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        followers = self.request.user.followers.all()
        followings = self.request.user.following.all()
        return Reel.objects.filter(Q(author__in=followers) | Q(author__in=followings) | Q(author=self.request.user))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status=status.HTTP_200_OK)


class ReelRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReelDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Reel.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(status=status.HTTP_204_NO_CONTENT)


class ReelCommentListCreateAPIView(ListCreateAPIView):
    serializer_class = CommentListCreateSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        reel = get_object_or_404(Reel, pk=self.kwargs['pk'])
        return ReelsComment.objects.filter(reel=reel)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data)

    def perform_create(self, serializer):
        reel = get_object_or_404(Reel, pk=self.kwargs['pk'])
        serializer.save(reel=reel, user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse.success(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReelCommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentRetrieveUpdateDestroySerializer
    queryset = ReelsComment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        comment = get_object_or_404(ReelsComment, id=self.kwargs.get('comment_id'))
        if comment.user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        return comment

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(status=status.HTTP_204_NO_CONTENT)

class ReelLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        reel = get_object_or_404(Reel, id=pk)
        if request.user in reel.likes.all():
            reel.likes.remove(request.user)
        else:
            reel.likes.add(request.user)
        reel.save()

        return CustomResponse.success(data={"likes_count": reel.likes.count()}, status=status.HTTP_200_OK)


class UserReelsListAPIView(ListAPIView):
    serializer_class = ReelListSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Reel.objects.filter(author=user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data)


