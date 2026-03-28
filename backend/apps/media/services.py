"""
Media services for BlogEngine.

Utility functions for file validation, image processing, and storage management.
"""

import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".md", ".csv", ".xlsx"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".avi", ".mov"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}

ALL_ALLOWED_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS
    | ALLOWED_DOCUMENT_EXTENSIONS
    | ALLOWED_VIDEO_EXTENSIONS
    | ALLOWED_AUDIO_EXTENSIONS
)


def validate_upload_size(uploaded_file, max_size_bytes=None):
    """
    Validate that an uploaded file does not exceed the maximum size.

    Returns an error message string if invalid, or None if valid.
    """
    if max_size_bytes is None:
        max_size_bytes = getattr(settings, "MAX_UPLOAD_SIZE_MB", 10) * 1024 * 1024

    if uploaded_file.size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        return f"File size exceeds the maximum allowed size of {max_mb:.0f} MB."
    return None


def validate_file_extension(filename):
    """
    Validate that the file extension is in the allow-list.

    Returns an error message string if invalid, or None if valid.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALL_ALLOWED_EXTENSIONS:
        return f"File extension '{ext}' is not allowed."
    return None


def detect_file_type(content_type, filename):
    """
    Determine the FileType enum value based on MIME type and extension.

    Returns a string matching MediaFile.FileType choices.
    """
    if content_type:
        if content_type.startswith("image/"):
            return "image"
        if content_type.startswith("video/"):
            return "video"
        if content_type.startswith("audio/"):
            return "audio"

    ext = os.path.splitext(filename)[1].lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return "image"
    if ext in ALLOWED_VIDEO_EXTENSIONS:
        return "video"
    if ext in ALLOWED_AUDIO_EXTENSIONS:
        return "audio"
    if ext in ALLOWED_DOCUMENT_EXTENSIONS:
        return "document"

    return "other"


def get_image_dimensions(uploaded_file):
    """
    Extract width and height from an image file.

    Returns (width, height) tuple or (None, None) if not an image.
    """
    try:
        from PIL import Image

        img = Image.open(uploaded_file)
        width, height = img.size
        uploaded_file.seek(0)  # Reset file pointer after reading
        return width, height
    except Exception:
        return None, None


def generate_thumbnail(media_file, max_dimension=300):
    """
    Generate a thumbnail for an image MediaFile instance.

    Creates a smaller version stored alongside the original.
    Returns the thumbnail path or None on failure.
    """
    if media_file.file_type != "image":
        return None

    try:
        from io import BytesIO

        from django.core.files.base import ContentFile
        from PIL import Image

        img = Image.open(media_file.file)
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        img_format = img.format or "JPEG"
        img.save(buffer, format=img_format)
        buffer.seek(0)

        thumb_name = f"thumb_{os.path.basename(media_file.file.name)}"
        thumb_path = os.path.join(os.path.dirname(media_file.file.name), thumb_name)

        from django.core.files.storage import default_storage

        saved_path = default_storage.save(thumb_path, ContentFile(buffer.read()))
        logger.info("Generated thumbnail: %s", saved_path)
        return saved_path
    except Exception as e:
        logger.error("Failed to generate thumbnail for %s: %s", media_file.id, e)
        return None


def cleanup_orphaned_files():
    """
    Find and remove files on disk that have no corresponding MediaFile record.

    Returns the count of deleted files.
    """
    from .models import MediaFile as MediaFileModel

    from django.core.files.storage import default_storage

    known_files = set(
        MediaFileModel.objects.values_list("file", flat=True)
    )

    deleted = 0
    media_root = str(settings.MEDIA_ROOT)
    uploads_dir = os.path.join(media_root, "uploads")

    if not os.path.exists(uploads_dir):
        return 0

    for dirpath, _dirnames, filenames in os.walk(uploads_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            relative = os.path.relpath(full_path, media_root).replace("\\", "/")
            if relative not in known_files:
                try:
                    default_storage.delete(relative)
                    deleted += 1
                except Exception as e:
                    logger.warning("Failed to delete orphan %s: %s", relative, e)

    logger.info("Cleaned up %d orphaned media files.", deleted)
    return deleted
