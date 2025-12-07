import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.register import RegisterSerializer
from apps.users.models import SendEmail

from django.core.mail import send_mail

User = get_user_model()

class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise CustomException(message_key="VALIDATION_ERROR")

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']

        user_exists = User.objects.filter(
            Q(username=username) | Q(email=email)
        ).exists()

        if user_exists:
            return CustomResponse.success(
                request=request,
                message_key="USER_ALREADY_EXISTS",
                status_code=status.HTTP_200_OK
            )
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            is_active=False
        )
        code = str(random.randint(100000, 999999))
        SendEmail.objects.filter(user=user).delete()

        SendEmail.objects.create(
            user=user,
            code=code,
            expired_at=datetime.now() + timedelta(minutes=10)
        )


        return CustomResponse.success(
            data={'code': code},
            request=request,
            message_key="USER_CREATED",
            status_code=status.HTTP_201_CREATED
        )


class VerifyAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            verify_obj = SendEmail.objects.get(user=user)
        except:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if verify_obj.code != code:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if verify_obj.expired_at < timezone.now():
            verify_obj.delete()
            user.delete()
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = True
        user.save()

        verify_obj.delete()

        return CustomResponse.success(
            request=request,
            message_key="EMAIL_VERIFIED",
            status_code=status.HTTP_200_OK
        )

