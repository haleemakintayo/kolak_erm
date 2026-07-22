from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateUpdateSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint — accepts username/email and password.
    Returns JWT access token, refresh token, and user profile.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserCreateUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """
    Change password for the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully."),
            400: OpenApiResponse(description="Validation error."),
        },
        description="Change password for the logged-in staff member."
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.must_change_password = False
        user.save()

        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)
