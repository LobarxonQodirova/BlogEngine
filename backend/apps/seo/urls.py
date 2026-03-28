"""URL configuration for the SEO app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "seo"

router = DefaultRouter()
router.register(r"metadata", views.SEOMetadataViewSet, basename="seo-metadata")
router.register(r"sitemap", views.SitemapViewSet, basename="sitemap")

urlpatterns = [
    path("", include(router.urls)),
]
