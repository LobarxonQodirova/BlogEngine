"""
Media models for BlogEngine.

Manages uploaded files (images, documents, videos) and gallery collections.
"""

import os
import uuid

from django.conf import settings
from django.db import models


def media_upload_path(instance, filename):
    """Generate a unique upload path: media/<year>/<month>/<uuid>.<ext>."""
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"uploads/{instance.uploaded_at.strftime('%Y/%m')}/{unique_name}"


class MediaFile(models.Model):
    """
    A single uploaded media file with metadata.

    Supports images, documents, audio, and video files.
    """

    class FileType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        AUDIO = "audio", "Audio"
        DOCUMENT = "document", "Document"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="uploads/%Y/%m/")
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.IMAGE,
    )
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="media_files",
    )
    gallery = models.ForeignKey(
        "Gallery",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
    )
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "media_file"
        ordering = ["-uploaded_at"]
        verbose_name = "media file"
        verbose_name_plural = "media files"

    def __str__(self):
        return self.title or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if not self.title and self.file:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def url(self):
        return self.file.url if self.file else ""

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ""

    @property
    def extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().lstrip(".")
        return ""


class Gallery(models.Model):
    """
    A named collection of media files, useful for organizing images
    by post, project, or album.
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    cover_image = models.ForeignKey(
        MediaFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cover_for_galleries",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="galleries",
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "media_gallery"
        verbose_name_plural = "galleries"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def file_count(self):
        return self.files.count()
