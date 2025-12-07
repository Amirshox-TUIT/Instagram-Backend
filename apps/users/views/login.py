from django.contrib.auth import  get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.login import LoginSerializer
from apps.users.serializers.profile import UserSerializer

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data['user']

        if not user.is_active:
            return CustomResponse.forbidden(
                status_code=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        user_serializer = UserSerializer(user, context={'request': request})

        return CustomResponse.success(
            message_key="LOGIN_SUCCESS",
            data={
                "access": access,
                "refresh": str(refresh),
                "user": user_serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return CustomResponse.error(
                    message_key="REFRESH_TOKEN_REQUIRED",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return CustomResponse.success(
                message_key="LOGOUT_SUCCESS",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return CustomResponse.error(
                message_key="LOGOUT_FAILED",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )


