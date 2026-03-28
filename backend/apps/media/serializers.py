"""
Media serializers for BlogEngine.

Handles serialization of MediaFile and Gallery models.
"""

from rest_framework import serializers

from .models import Gallery, MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()
    extension = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )

    class Meta:
        model = MediaFile
        fields = [
            "id",
            "title",
            "file",
            "file_type",
            "mime_type",
            "file_size",
            "width",
            "height",
            "alt_text",
            "caption",
            "uploaded_by",
            "uploaded_by_name",
            "gallery",
            "is_public",
            "url",
            "filename",
            "extension",
            "uploaded_at",
        ]
        read_only_fields = ["uploaded_by", "file_size", "mime_type"]


class MediaFileUploadSerializer(serializers.ModelSerializer):
    """Simplified serializer for file upload with auto-detection."""

    class Meta:
        model = MediaFile
        fields = ["file", "title", "alt_text", "caption", "gallery", "is_public"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["uploaded_by"] = request.user

        uploaded_file = validated_data.get("file")
        if uploaded_file:
            content_type = uploaded_file.content_type or ""
            validated_data["mime_type"] = content_type
            validated_data["file_size"] = uploaded_file.size

            if content_type.startswith("image/"):
                validated_data["file_type"] = MediaFile.FileType.IMAGE
                try:
                    from PIL import Image

                    img = Image.open(uploaded_file)
                    validated_data["width"], validated_data["height"] = img.size
                except Exception:
                    pass
            elif content_type.startswith("video/"):
                validated_data["file_type"] = MediaFile.FileType.VIDEO
            elif content_type.startswith("audio/"):
                validated_data["file_type"] = MediaFile.FileType.AUDIO
            else:
                validated_data["file_type"] = MediaFile.FileType.DOCUMENT

        return super().create(validated_data)


class GallerySerializer(serializers.ModelSerializer):
    file_count = serializers.ReadOnlyField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "cover_image",
            "cover_image_url",
            "owner",
            "is_public",
            "file_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "slug"]

    def get_cover_image_url(self, obj):
        if obj.cover_image and obj.cover_image.file:
            return obj.cover_image.file.url
        return None


class GalleryDetailSerializer(GallerySerializer):
    files = MediaFileSerializer(many=True, read_only=True)

    class Meta(GallerySerializer.Meta):
        fields = GallerySerializer.Meta.fields + ["files"]
