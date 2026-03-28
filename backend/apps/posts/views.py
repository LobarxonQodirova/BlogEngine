"""
Post views for BlogEngine.

ViewSets and APIViews for managing posts, categories, tags, and series.
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAuthor, IsOwnerOrEditor

from .models import Category, Post, PostComment, PostLike, PostView, Series, Tag
from .serializers import (
    CategorySerializer,
    PostCommentSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostLikeSerializer,
    PostListSerializer,
    SeriesSerializer,
    TagSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for blog posts.

    list:   Returns published posts (public) or all posts for the author.
    create: Requires authentication (author role).
    update: Only the author or editors can modify.
    """

    lookup_field = "slug"
    search_fields = ["title", "content", "excerpt"]
    ordering_fields = ["published_at", "created_at", "view_count", "like_count"]
    filterset_fields = ["status", "category", "is_featured", "author"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PostCreateUpdateSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.action in ("create",):
            return [IsAuthor()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsOwnerOrEditor()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = Post.objects.select_related("author", "category", "series").prefetch_related(
            "tags", "custom_tags"
        )
        if self.request.user.is_authenticated and self.request.query_params.get("mine"):
            return qs.filter(author=self.request.user)
        if self.action == "list":
            return qs.filter(status="published")
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Track view
        PostView.objects.create(
            post=instance,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referrer=request.META.get("HTTP_REFERER", ""),
        )
        instance.view_count += 1
        instance.save(update_fields=["view_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        """Toggle like on a post."""
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            post.like_count = max(0, post.like_count - 1)
            post.save(update_fields=["like_count"])
            return Response({"liked": False, "like_count": post.like_count})
        post.like_count += 1
        post.save(update_fields=["like_count"])
        return Response({"liked": True, "like_count": post.like_count})

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Return featured posts."""
        qs = self.get_queryset().filter(is_featured=True, status="published")[:6]
        serializer = PostListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Full-text search across posts."""
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([])
        qs = (
            self.get_queryset()
            .filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(excerpt__icontains=query),
                status="published",
            )[:20]
        )
        serializer = PostListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD for post categories."""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class TagViewSet(viewsets.ModelViewSet):
    """CRUD for post tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class SeriesViewSet(viewsets.ModelViewSet):
    """CRUD for post series."""

    queryset = Series.objects.select_related("author").all()
    serializer_class = SeriesSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("create",):
            return [IsAuthor()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsOwnerOrEditor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["get"])
    def posts(self, request, slug=None):
        """List all published posts in a series, ordered."""
        series = self.get_object()
        posts = Post.objects.filter(
            series=series, status="published"
        ).order_by("series_order")
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)


class PostCommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/posts/<slug>/comments/  - list comments for a post
    POST /api/posts/<slug>/comments/  - add a comment
    """

    serializer_class = PostCommentSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return PostComment.objects.filter(
            post__slug=self.kwargs["slug"],
            is_approved=True,
        ).select_related("author")

    def perform_create(self, serializer):
        post = Post.objects.get(slug=self.kwargs["slug"])
        serializer.save(author=self.request.user, post=post)
        post.comment_count += 1
        post.save(update_fields=["comment_count"])
