"""
Post serializers for BlogEngine.

Handles serialization of Post, Category, Tag, Series, and related models.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Category, Post, PostComment, PostLike, PostView, Series, Tag

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.ReadOnlyField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "icon",
            "color",
            "order",
            "is_active",
            "post_count",
            "children",
        ]
        read_only_fields = ["slug"]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "description"]
        read_only_fields = ["slug"]


class SeriesSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    post_count = serializers.ReadOnlyField()

    class Meta:
        model = Series
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "cover_image",
            "author",
            "author_name",
            "is_completed",
            "post_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "author"]


class PostAuthorSerializer(serializers.ModelSerializer):
    """Compact author representation embedded in post responses."""

    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "username", "display_name", "slug", "avatar"]


class PostListSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for post list views (compact, no full content)."""

    author = PostAuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField()
    short_excerpt = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "subtitle",
            "short_excerpt",
            "featured_image",
            "author",
            "category",
            "tags",
            "status",
            "is_featured",
            "is_pinned",
            "reading_time_minutes",
            "view_count",
            "like_count",
            "comment_count",
            "published_at",
            "created_at",
        ]


class PostDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Full post serializer with all content and metadata."""

    author = PostAuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    series = SeriesSerializer(read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "subtitle",
            "content",
            "excerpt",
            "featured_image",
            "featured_image_alt",
            "author",
            "category",
            "tags",
            "series",
            "series_order",
            "status",
            "is_featured",
            "is_pinned",
            "allow_comments",
            "reading_time_minutes",
            "view_count",
            "like_count",
            "comment_count",
            "meta_title",
            "meta_description",
            "canonical_url",
            "published_at",
            "scheduled_at",
            "created_at",
            "updated_at",
        ]


class PostCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for creating and updating posts."""

    tags = TagListSerializerField(required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        required=False,
        allow_null=True,
    )
    series_id = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(),
        source="series",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "subtitle",
            "content",
            "excerpt",
            "featured_image",
            "featured_image_alt",
            "category_id",
            "tags",
            "series_id",
            "series_order",
            "status",
            "is_featured",
            "is_pinned",
            "allow_comments",
            "meta_title",
            "meta_description",
            "canonical_url",
            "scheduled_at",
        ]

    def validate_scheduled_at(self, value):
        from django.utils import timezone

        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)

    class Meta:
        model = PostComment
        fields = [
            "id",
            "post",
            "author",
            "author_name",
            "body",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "is_approved"]


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ["id", "post", "user", "created_at"]
        read_only_fields = ["user"]


class PostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostView
        fields = ["id", "post", "user", "ip_address", "viewed_at"]
        read_only_fields = ["user", "ip_address"]
