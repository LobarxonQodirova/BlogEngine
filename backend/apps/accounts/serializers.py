"""
Account serializers for BlogEngine.

Handles user registration, login, profile management, and author listings.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuthorProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for new user registration with password confirmation."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        AuthorProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for authenticating users via email + password."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Full profile serializer for the authenticated user."""

    display_name = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "bio",
            "avatar",
            "website",
            "twitter_handle",
            "github_handle",
            "slug",
            "display_name",
            "post_count",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "slug", "is_verified", "date_joined"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating the authenticated user's profile fields."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "bio",
            "avatar",
            "website",
            "twitter_handle",
            "github_handle",
        ]


class AuthorProfileSerializer(serializers.ModelSerializer):
    """Serializer for the extended author profile."""

    class Meta:
        model = AuthorProfile
        fields = [
            "tagline",
            "location",
            "company",
            "is_featured",
            "expertise",
            "social_links",
            "total_views",
            "total_likes",
        ]
        read_only_fields = ["total_views", "total_likes"]


class AuthorListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing authors publicly."""

    author_profile = AuthorProfileSerializer(read_only=True)
    post_count = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "display_name",
            "slug",
            "avatar",
            "bio",
            "author_profile",
            "post_count",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing the authenticated user's password."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs
