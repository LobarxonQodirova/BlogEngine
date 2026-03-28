"""
Custom permissions for BlogEngine accounts.

Role-based permission classes for Author, Editor, and Admin roles.
"""

from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    """Allows access only to users with the Author role (or higher)."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("author", "editor", "admin")
        )


class IsEditor(BasePermission):
    """Allows access only to users with the Editor role (or higher)."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("editor", "admin")
        )


class IsAdminUser(BasePermission):
    """Allows access only to users with the Admin role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: only the owner can modify.

    Expects the object to have an `author` or `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        owner = getattr(obj, "author", None) or getattr(obj, "user", None)
        return owner == request.user


class IsOwnerOrEditor(BasePermission):
    """
    Object-level permission: the owner or any Editor/Admin can modify.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        owner = getattr(obj, "author", None) or getattr(obj, "user", None)
        if owner == request.user:
            return True
        return request.user.role in ("editor", "admin")


class IsVerifiedAuthor(BasePermission):
    """Only verified authors can publish posts."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
