"""
Analytics views for BlogEngine.

Dashboard endpoints for post-level and site-wide analytics.
"""

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAuthor, IsEditor

from .models import PageView, PostAnalytics, SiteAnalytics
from .services import get_post_analytics_summary, get_site_dashboard_data


class PostAnalyticsView(APIView):
    """
    GET /api/analytics/posts/<slug>/
    Returns analytics data for a specific post (author or editor).
    """

    permission_classes = [IsAuthor]

    def get(self, request, slug):
        from apps.posts.models import Post

        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=404)

        # Only the author or editors can view analytics
        if post.author != request.user and request.user.role not in ("editor", "admin"):
            return Response({"detail": "Forbidden."}, status=403)

        days = int(request.query_params.get("days", 30))
        data = get_post_analytics_summary(post, days)
        return Response(data)


class DashboardAnalyticsView(APIView):
    """
    GET /api/analytics/dashboard/
    Returns aggregated analytics for the author's dashboard.
    """

    permission_classes = [IsAuthor]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        since = timezone.now().date() - timedelta(days=days)

        # For authors: their own posts' analytics
        # For editors/admins: all posts
        if request.user.role in ("editor", "admin"):
            post_analytics = PostAnalytics.objects.filter(date__gte=since)
        else:
            post_analytics = PostAnalytics.objects.filter(
                post__author=request.user, date__gte=since
            )

        totals = post_analytics.aggregate(
            total_views=Sum("views"),
            total_unique=Sum("unique_visitors"),
            total_likes=Sum("likes"),
            total_comments=Sum("comments"),
        )

        # Daily trend
        daily = (
            post_analytics.values("date")
            .annotate(
                day_views=Sum("views"),
                day_unique=Sum("unique_visitors"),
            )
            .order_by("date")
        )

        # Top posts
        from apps.posts.models import Post

        if request.user.role in ("editor", "admin"):
            top_posts = Post.objects.filter(status="published").order_by("-view_count")[:5]
        else:
            top_posts = Post.objects.filter(
                author=request.user, status="published"
            ).order_by("-view_count")[:5]

        top_posts_data = [
            {
                "title": p.title,
                "slug": p.slug,
                "views": p.view_count,
                "likes": p.like_count,
            }
            for p in top_posts
        ]

        return Response(
            {
                "period_days": days,
                "totals": {
                    "views": totals["total_views"] or 0,
                    "unique_visitors": totals["total_unique"] or 0,
                    "likes": totals["total_likes"] or 0,
                    "comments": totals["total_comments"] or 0,
                },
                "daily_trend": list(daily),
                "top_posts": top_posts_data,
            }
        )


class SiteDashboardView(APIView):
    """
    GET /api/analytics/site/
    Admin-only: site-wide analytics dashboard.
    """

    permission_classes = [IsEditor]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        data = get_site_dashboard_data(days)
        return Response(data)


class TrackPageView(APIView):
    """
    POST /api/analytics/track/
    Record a page view from the frontend.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        path = request.data.get("path", "")
        if not path:
            return Response(
                {"detail": "path is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        PageView.objects.create(
            path=path,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            referrer=request.META.get("HTTP_REFERER", "")[:200],
        )
        return Response({"detail": "Tracked."}, status=status.HTTP_201_CREATED)
