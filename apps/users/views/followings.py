from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.profile import UserSerializer
from django.shortcuts import get_object_or_404

User = get_user_model()


class UserFollowingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return CustomResponse.error(
                message_key="USER_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        followings = user.following.all()
        serializer = UserSerializer(followings, many=True)

        return CustomResponse.success(
            message_key="FOLLOWINGS_FETCHED",
            data={"followings": serializer.data},
            status_code=status.HTTP_200_OK
        )


class UserFollowersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return CustomResponse.error(
                message_key="USER_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)

        return CustomResponse.success(
            message_key="FOLLOWERS_FETCHED",
            data={"followers": serializer.data},
            status_code=status.HTTP_200_OK
        )


class FollowUnfollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, username):
        target_user = get_object_or_404(User, username=username)
        current_user = request.user

        if target_user == current_user:
            return CustomResponse.error(
                message_key="CANNOT_FOLLOW_YOURSELF",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if target_user in current_user.following.all():
            current_user.following.remove(target_user)
            action = "unfollowed"
        else:
            current_user.following.add(target_user)
            action = "followed"

        current_user.save()

        return CustomResponse.success(
            message_key=f"{action.upper()}_SUCCESS",
            data={
                "user_id": target_user.id,
                "username": target_user.username,
                "action": action
            },
            status_code=status.HTTP_200_OK
        )
