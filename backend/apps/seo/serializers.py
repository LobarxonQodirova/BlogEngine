"""
SEO serializers for BlogEngine.

Handles serialization of SEOMetadata and Sitemap models.
"""

from rest_framework import serializers

from .models import SEOMetadata, Sitemap


class SEOMetadataSerializer(serializers.ModelSerializer):
    robots_directives = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = SEOMetadata
        fields = [
            "id",
            "content_type",
            "object_id",
            "content_type_name",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "canonical_url",
            "og_title",
            "og_description",
            "og_image",
            "og_type",
            "twitter_card",
            "twitter_title",
            "twitter_description",
            "twitter_image",
            "structured_data",
            "no_index",
            "no_follow",
            "robots_directives",
            "created_at",
            "updated_at",
        ]

    def get_content_type_name(self, obj):
        return f"{obj.content_type.app_label}.{obj.content_type.model}"


class SEOMetadataCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating SEO metadata for a specific object."""

    class Meta:
        model = SEOMetadata
        fields = [
            "content_type",
            "object_id",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "canonical_url",
            "og_title",
            "og_description",
            "og_image",
            "og_type",
            "twitter_card",
            "twitter_title",
            "twitter_description",
            "twitter_image",
            "structured_data",
            "no_index",
            "no_follow",
        ]


class SitemapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitemap
        fields = [
            "id",
            "url",
            "title",
            "priority",
            "change_frequency",
            "last_modified",
            "is_active",
            "created_at",
        ]
