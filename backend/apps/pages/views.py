"""
Page views for BlogEngine.

ViewSets for managing CMS pages and page templates.
"""

from rest_framework import permissions, viewsets

from apps.accounts.permissions import IsEditor, IsOwnerOrEditor

from .models import Page, PageTemplate
from .serializers import (
    PageCreateUpdateSerializer,
    PageDetailSerializer,
    PageListSerializer,
    PageTemplateSerializer,
)


class PageViewSet(viewsets.ModelViewSet):
    """
    CRUD for CMS pages.

    Public users see published pages; editors can manage all pages.
    """

    lookup_field = "slug"
    search_fields = ["title", "content"]
    filterset_fields = ["status", "show_in_menu", "template"]
    ordering_fields = ["menu_order", "title", "created_at"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PageCreateUpdateSerializer
        if self.action == "retrieve":
            return PageDetailSerializer
        return PageListSerializer

    def get_permissions(self):
        if self.action in ("create",):
            return [IsEditor()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsOwnerOrEditor()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = Page.objects.select_related("author", "template", "parent")
        if self.action == "list" and not (
            self.request.user.is_authenticated
            and self.request.user.role in ("editor", "admin")
        ):
            return qs.filter(status="published")
        return qs


class PageTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for page templates (admin-only for modifications).
    """

    queryset = PageTemplate.objects.filter(is_active=True)
    serializer_class = PageTemplateSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class MenuPagesView(viewsets.GenericViewSet):
    """
    GET /api/pages/menu/
    Returns pages flagged for menu display, ordered by menu_order.
    """

    serializer_class = PageListSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        pages = Page.objects.filter(
            status="published",
            show_in_menu=True,
        ).order_by("menu_order")
        serializer = self.get_serializer(pages, many=True)
        from rest_framework.response import Response

        return Response(serializer.data)
