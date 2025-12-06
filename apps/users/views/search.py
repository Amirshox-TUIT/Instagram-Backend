from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.profile import UserSerializer

User = get_user_model()


class SearchUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.query_params.get('search', '')

        if not search_query:
            return CustomResponse.error(
                message_key="SEARCH_QUERY_REQUIRED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).exclude(id=request.user.id)[:10]
        serializer = UserSerializer(users, many=True)

        return CustomResponse.success(
            message_key="USERS_FOUND",
            data={"users": serializer.data},
            status_code=status.HTTP_200_OK
        )