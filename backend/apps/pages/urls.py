"""URL configuration for the pages app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "pages"

router = DefaultRouter()
router.register(r"pages", views.PageViewSet, basename="page")
router.register(r"templates", views.PageTemplateViewSet, basename="page-template")
router.register(r"menu", views.MenuPagesView, basename="menu-pages")

urlpatterns = [
    path("", include(router.urls)),
]
