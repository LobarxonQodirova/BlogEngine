"""URL configuration for the analytics app."""

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path(
        "posts/<slug:slug>/",
        views.PostAnalyticsView.as_view(),
        name="post-analytics",
    ),
    path(
        "dashboard/",
        views.DashboardAnalyticsView.as_view(),
        name="dashboard-analytics",
    ),
    path("site/", views.SiteDashboardView.as_view(), name="site-dashboard"),
    path("track/", views.TrackPageView.as_view(), name="track-pageview"),
]
