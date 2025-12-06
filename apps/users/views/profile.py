from django.contrib.auth import get_user_model
from rest_framework.generics import UpdateAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.serializers.profile import UserSerializer, UserUpdateSerializer

User = get_user_model()

class ProfileDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [AllowAny]


class UserProfileUpdateAPIView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        if user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        return user
