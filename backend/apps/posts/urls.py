"""URL configuration for the posts app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "posts"

router = DefaultRouter()
router.register(r"posts", views.PostViewSet, basename="post")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"tags", views.TagViewSet, basename="tag")
router.register(r"series", views.SeriesViewSet, basename="series")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<slug:slug>/comments/",
        views.PostCommentListCreateView.as_view(),
        name="post-comments",
    ),
]
