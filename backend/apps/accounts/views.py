"""
Account views for BlogEngine.

Handles registration, authentication, profile CRUD, and author listings.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsAdminUser
from .serializers import (
    AuthorListSerializer,
    AuthorProfileSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user account and return JWT tokens.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Obtain JWT access and refresh tokens.
    """

    permission_classes = [permissions.AllowAny]


class TokenRefreshAPIView(TokenRefreshView):
    """
    POST /api/auth/token/refresh/
    Refresh an expired access token using a valid refresh token.
    """

    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklist the provided refresh token to log the user out.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/auth/profile/
    Retrieve or update the authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user


class AuthorProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/auth/author-profile/
    Retrieve or update the authenticated user's author profile.
    """

    serializer_class = AuthorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = self.request.user.author_profile.__class__.objects.get_or_create(
            user=self.request.user
        )
        return profile


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Change the authenticated user's password.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class AuthorListView(generics.ListAPIView):
    """
    GET /api/auth/authors/
    List all authors publicly.
    """

    serializer_class = AuthorListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.filter(
        role__in=["author", "editor", "admin"],
        is_active=True,
    ).select_related("author_profile")
    search_fields = ["username", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined"]


class AuthorDetailView(generics.RetrieveAPIView):
    """
    GET /api/auth/authors/<slug>/
    Retrieve a single author profile by slug.
    """

    serializer_class = AuthorListSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    queryset = User.objects.filter(
        is_active=True,
    ).select_related("author_profile")


class UserManagementView(generics.ListAPIView):
    """
    GET /api/auth/users/
    Admin-only: list all users for management.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-date_joined")
    filterset_fields = ["role", "is_active", "is_verified"]
    search_fields = ["username", "email", "first_name", "last_name"]
