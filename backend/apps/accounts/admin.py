"""Admin configuration for the accounts app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuthorProfile, User


class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    can_delete = False
    verbose_name = "Author Profile"
    verbose_name_plural = "Author Profile"
    fields = (
        "tagline",
        "location",
        "company",
        "is_featured",
        "expertise",
        "social_links",
        "total_views",
        "total_likes",
    )
    readonly_fields = ("total_views", "total_likes")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_verified",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_verified", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    inlines = [AuthorProfileInline]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "BlogEngine Fields",
            {
                "fields": (
                    "role",
                    "bio",
                    "avatar",
                    "website",
                    "twitter_handle",
                    "github_handle",
                    "slug",
                    "is_verified",
                    "email_verified",
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "BlogEngine Fields",
            {
                "fields": ("email", "role"),
            },
        ),
    )
