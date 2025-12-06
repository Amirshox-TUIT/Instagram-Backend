from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.posts.serializers.post_create import CreatePostSerializer
from apps.posts.serializers.post_list import PostSerializer
from apps.shared.utils.custom_response import CustomResponse


class CreatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePostSerializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        post = serializer.save(author=request.user)

        response_serializer = PostSerializer(post, context={'request': request})

        return CustomResponse.success(
            message_key="POST_CREATED",
            data={"post": response_serializer.data},
            status_code=status.HTTP_201_CREATED
        )