"""
Analytics services for BlogEngine.

Aggregation utilities and dashboard data generators.
"""

import logging
from collections import Counter
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_post_analytics_summary(post, days=30):
    """
    Build an analytics summary for a single post over the past N days.

    Returns views, unique visitors, likes, daily trend, and referrer breakdown.
    """
    from apps.posts.models import PostView

    from .models import PostAnalytics

    since = timezone.now().date() - timedelta(days=days)

    # Aggregated daily analytics
    daily = (
        PostAnalytics.objects.filter(post=post, date__gte=since)
        .values("date")
        .annotate(
            day_views=Sum("views"),
            day_unique=Sum("unique_visitors"),
            day_likes=Sum("likes"),
        )
        .order_by("date")
    )

    # Total counts
    totals = PostAnalytics.objects.filter(
        post=post, date__gte=since
    ).aggregate(
        total_views=Sum("views"),
        total_unique=Sum("unique_visitors"),
        total_likes=Sum("likes"),
        total_comments=Sum("comments"),
    )

    # Top referrers from raw view data
    referrers = (
        PostView.objects.filter(
            post=post,
            viewed_at__date__gte=since,
            referrer__gt="",
        )
        .values("referrer")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    return {
        "post": {
            "title": post.title,
            "slug": post.slug,
            "published_at": post.published_at,
        },
        "period_days": days,
        "totals": {
            "views": totals["total_views"] or 0,
            "unique_visitors": totals["total_unique"] or 0,
            "likes": totals["total_likes"] or 0,
            "comments": totals["total_comments"] or 0,
        },
        "daily_trend": list(daily),
        "top_referrers": list(referrers),
    }


def get_site_dashboard_data(days=30):
    """
    Build site-wide dashboard analytics data.

    Aggregates page views, new content counts, and device breakdown.
    """
    from .models import PageView, SiteAnalytics

    since = timezone.now().date() - timedelta(days=days)

    # Try pre-aggregated data first
    site_data = SiteAnalytics.objects.filter(date__gte=since).order_by("date")

    if site_data.exists():
        totals = site_data.aggregate(
            total_views=Sum("total_views"),
            total_unique=Sum("unique_visitors"),
            total_new_subs=Sum("new_subscribers"),
            total_new_posts=Sum("new_posts"),
            total_new_comments=Sum("new_comments"),
        )

        daily = site_data.values(
            "date", "total_views", "unique_visitors"
        )

        return {
            "period_days": days,
            "totals": {
                "views": totals["total_views"] or 0,
                "unique_visitors": totals["total_unique"] or 0,
                "new_subscribers": totals["total_new_subs"] or 0,
                "new_posts": totals["total_new_posts"] or 0,
                "new_comments": totals["total_new_comments"] or 0,
            },
            "daily_trend": list(daily),
        }

    # Fallback: compute from raw PageView data
    since_dt = timezone.now() - timedelta(days=days)
    raw_views = PageView.objects.filter(viewed_at__gte=since_dt)

    total_views = raw_views.count()
    unique_ips = raw_views.values("ip_address").distinct().count()

    # Top pages
    top_pages = (
        raw_views.values("path")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Device breakdown
    devices = raw_views.exclude(device_type="").values("device_type").annotate(
        count=Count("id")
    )
    device_map = {d["device_type"]: d["count"] for d in devices}

    return {
        "period_days": days,
        "totals": {
            "views": total_views,
            "unique_visitors": unique_ips,
        },
        "top_pages": list(top_pages),
        "device_breakdown": device_map,
    }


def aggregate_daily_analytics():
    """
    Aggregate yesterday's raw data into PostAnalytics and SiteAnalytics rows.

    Called daily by Celery Beat.
    """
    from apps.posts.models import Post, PostComment, PostLike, PostView

    from .models import PageView, PostAnalytics, SiteAnalytics

    yesterday = timezone.now().date() - timedelta(days=1)

    # Per-post aggregation
    posts_with_views = (
        PostView.objects.filter(viewed_at__date=yesterday)
        .values("post_id")
        .annotate(
            view_count=Count("id"),
            unique_count=Count("ip_address", distinct=True),
        )
    )

    for entry in posts_with_views:
        post_id = entry["post_id"]
        likes = PostLike.objects.filter(
            post_id=post_id, created_at__date=yesterday
        ).count()
        comments = PostComment.objects.filter(
            post_id=post_id, created_at__date=yesterday, is_approved=True
        ).count()

        PostAnalytics.objects.update_or_create(
            post_id=post_id,
            date=yesterday,
            defaults={
                "views": entry["view_count"],
                "unique_visitors": entry["unique_count"],
                "likes": likes,
                "comments": comments,
            },
        )

    # Site-wide aggregation
    total_page_views = PageView.objects.filter(viewed_at__date=yesterday).count()
    unique_visitors = (
        PageView.objects.filter(viewed_at__date=yesterday)
        .values("ip_address")
        .distinct()
        .count()
    )
    new_posts = Post.objects.filter(
        published_at__date=yesterday, status="published"
    ).count()

    SiteAnalytics.objects.update_or_create(
        date=yesterday,
        defaults={
            "total_views": total_page_views,
            "unique_visitors": unique_visitors,
            "new_posts": new_posts,
        },
    )

    logger.info("Aggregated analytics for %s.", yesterday)
