"""URL configuration for the media app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "media"

router = DefaultRouter()
router.register(r"files", views.MediaFileViewSet, basename="media-file")
router.register(r"galleries", views.GalleryViewSet, basename="gallery")

urlpatterns = [
    path("", include(router.urls)),
    path("upload/", views.MediaUploadView.as_view(), name="media-upload"),
]
