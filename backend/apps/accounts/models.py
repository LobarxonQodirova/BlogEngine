"""
Account models for BlogEngine.

Custom User model with role-based access: Author, Editor, Admin.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify


class UserManager(BaseUserManager):
    """Custom manager for the User model supporting email-based creation."""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with role-based permissions.

    Roles:
    - AUTHOR: Can create and manage own posts
    - EDITOR: Can edit and publish any post
    - ADMIN: Full platform access
    """

    class Role(models.TextChoices):
        AUTHOR = "author", "Author"
        EDITOR = "editor", "Editor"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.AUTHOR,
    )
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)
    website = models.URLField(max_length=200, blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    github_handle = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "accounts_user"
        ordering = ["-created_at"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    @property
    def is_author(self):
        return self.role == self.Role.AUTHOR

    @property
    def is_editor(self):
        return self.role == self.Role.EDITOR

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def display_name(self):
        full = self.get_full_name()
        return full if full else self.username

    @property
    def post_count(self):
        return self.posts.filter(status="published").count()


class AuthorProfile(models.Model):
    """
    Extended profile for authors with social links and author-specific metadata.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    tagline = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    expertise = models.JSONField(default=list, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "accounts_author_profile"
        verbose_name = "author profile"
        verbose_name_plural = "author profiles"

    def __str__(self):
        return f"Profile of {self.user.username}"
