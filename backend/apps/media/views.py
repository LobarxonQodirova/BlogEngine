"""
Media views for BlogEngine.

Handles file upload, listing, deletion, and gallery management.
"""

from django.conf import settings
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwnerOrReadOnly

from .models import Gallery, MediaFile
from .serializers import (
    GalleryDetailSerializer,
    GallerySerializer,
    MediaFileSerializer,
    MediaFileUploadSerializer,
)
from .services import validate_upload_size


class MediaFileViewSet(viewsets.ModelViewSet):
    """
    CRUD for media files.

    Supports listing, uploading, updating metadata, and deleting files.
    """

    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ["file_type", "gallery", "is_public"]
    search_fields = ["title", "alt_text", "caption"]
    ordering_fields = ["uploaded_at", "file_size", "title"]

    def get_queryset(self):
        qs = MediaFile.objects.select_related("uploaded_by", "gallery")
        if not self.request.user.is_staff:
            return qs.filter(uploaded_by=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return MediaFileUploadSerializer
        return MediaFileSerializer

    def perform_destroy(self, instance):
        # Delete the actual file from storage
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


class MediaUploadView(APIView):
    """
    POST /api/media/upload/
    Upload one or more files. Accepts multipart/form-data.
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        files = request.FILES.getlist("files")
        if not files:
            files = [request.FILES.get("file")]
            if not files[0]:
                return Response(
                    {"detail": "No files provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        max_size = getattr(settings, "MAX_UPLOAD_SIZE_MB", 10) * 1024 * 1024
        uploaded = []
        errors = []

        for f in files:
            error = validate_upload_size(f, max_size)
            if error:
                errors.append({"file": f.name, "error": error})
                continue

            serializer = MediaFileUploadSerializer(
                data={"file": f, "title": f.name},
                context={"request": request},
            )
            if serializer.is_valid():
                media_file = serializer.save()
                uploaded.append(MediaFileSerializer(media_file).data)
            else:
                errors.append({"file": f.name, "error": serializer.errors})

        return Response(
            {"uploaded": uploaded, "errors": errors},
            status=status.HTTP_201_CREATED if uploaded else status.HTTP_400_BAD_REQUEST,
        )


class GalleryViewSet(viewsets.ModelViewSet):
    """CRUD for galleries."""

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filterset_fields = ["is_public"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        qs = Gallery.objects.select_related("owner", "cover_image")
        if not self.request.user.is_staff:
            return qs.filter(owner=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GalleryDetailSerializer
        return GallerySerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
