from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.register import RegisterSerializer

User = get_user_model()
class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']
        user_exists = User.objects.filter(Q(username=username)|Q(email=email)).exists()

        if not user_exists:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
            )
            created = True

        else:
            created = False

        message_key = "USER_CREATED" if created else "USER_ALREADY_EXISTS"

        return CustomResponse.success(
            request=request,
            message_key=message_key,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )