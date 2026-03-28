"""
Page serializers for BlogEngine.

Handles serialization of Page and PageTemplate models.
"""

from rest_framework import serializers

from .models import Page, PageTemplate


class PageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageTemplate
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "html_structure",
            "thumbnail",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["slug"]


class PageListSerializer(serializers.ModelSerializer):
    """Compact serializer for page listings."""

    author_name = serializers.CharField(source="author.display_name", read_only=True)
    template_name = serializers.CharField(source="template.name", read_only=True, default=None)

    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "featured_image",
            "author_name",
            "template_name",
            "status",
            "show_in_menu",
            "menu_order",
            "published_at",
            "updated_at",
        ]


class PageDetailSerializer(serializers.ModelSerializer):
    """Full serializer for page detail views."""

    author_name = serializers.CharField(source="author.display_name", read_only=True)
    template = PageTemplateSerializer(read_only=True)
    full_path = serializers.ReadOnlyField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "featured_image",
            "template",
            "author",
            "author_name",
            "status",
            "show_in_menu",
            "menu_order",
            "parent",
            "children",
            "meta_title",
            "meta_description",
            "full_path",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "slug"]

    def get_children(self, obj):
        children = obj.children.filter(status="published")
        return PageListSerializer(children, many=True).data


class PageCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating pages."""

    template_id = serializers.PrimaryKeyRelatedField(
        queryset=PageTemplate.objects.filter(is_active=True),
        source="template",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Page
        fields = [
            "title",
            "content",
            "excerpt",
            "featured_image",
            "template_id",
            "status",
            "show_in_menu",
            "menu_order",
            "parent",
            "meta_title",
            "meta_description",
        ]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
