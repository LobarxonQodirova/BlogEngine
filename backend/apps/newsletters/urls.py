"""URL configuration for the newsletters app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "newsletters"

router = DefaultRouter()
router.register(r"newsletters", views.NewsletterViewSet, basename="newsletter")
router.register(r"campaigns", views.CampaignViewSet, basename="campaign")

urlpatterns = [
    path("subscribe/", views.SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", views.UnsubscribeView.as_view(), name="unsubscribe"),
    path("subscribers/", views.SubscriberListView.as_view(), name="subscriber-list"),
    path(
        "campaigns/send/",
        views.CampaignSendView.as_view(),
        name="campaign-send",
    ),
    path("", include(router.urls)),
]
