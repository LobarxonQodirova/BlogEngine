"""
SEO views for BlogEngine.

ViewSets for managing SEO metadata and sitemap entries.
"""

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SEOMetadata, Sitemap
from .serializers import (
    SEOMetadataCreateSerializer,
    SEOMetadataSerializer,
    SitemapSerializer,
)
from .services import generate_structured_data_for_post


class SEOMetadataViewSet(viewsets.ModelViewSet):
    """
    CRUD for SEO metadata entries.

    Admin/Editor only for modifications; read-only for SEO consumption.
    """

    queryset = SEOMetadata.objects.select_related("content_type").all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return SEOMetadataCreateSerializer
        return SEOMetadataSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=["get"])
    def for_object(self, request):
        """
        GET /api/seo/metadata/for_object/?content_type=posts.post&object_id=42
        Retrieve SEO metadata for a specific content object.
        """
        ct_label = request.query_params.get("content_type", "")
        object_id = request.query_params.get("object_id")

        if not ct_label or not object_id:
            return Response(
                {"detail": "content_type and object_id are required."},
                status=400,
            )

        try:
            app_label, model = ct_label.split(".")
            from django.contrib.contenttypes.models import ContentType

            ct = ContentType.objects.get(app_label=app_label, model=model)
            seo = SEOMetadata.objects.get(content_type=ct, object_id=object_id)
            return Response(SEOMetadataSerializer(seo).data)
        except (ValueError, SEOMetadata.DoesNotExist):
            return Response({"detail": "Not found."}, status=404)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def generate_for_post(self, request):
        """
        POST /api/seo/metadata/generate_for_post/
        Auto-generate SEO metadata and structured data for a post.
        """
        post_id = request.data.get("post_id")
        if not post_id:
            return Response({"detail": "post_id is required."}, status=400)

        try:
            from apps.posts.models import Post

            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=404)

        seo_data = generate_structured_data_for_post(post)
        return Response(seo_data)


class SitemapViewSet(viewsets.ModelViewSet):
    """
    CRUD for custom sitemap entries.

    Admin-only for modifications; the XML sitemap is generated via services.
    """

    queryset = Sitemap.objects.filter(is_active=True)
    serializer_class = SitemapSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
