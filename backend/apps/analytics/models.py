"""
Analytics models for BlogEngine.

Tracks page views, post engagement, and aggregated analytics data.
"""

from django.conf import settings
from django.db import models


class PageView(models.Model):
    """
    Records every page view across the site for general analytics.

    Different from PostView which is post-specific.
    """

    path = models.CharField(max_length=500, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    country = models.CharField(max_length=2, blank=True, help_text="ISO country code")
    device_type = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
        ],
    )
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "analytics_page_view"
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["path", "-viewed_at"]),
        ]

    def __str__(self):
        return f"{self.path} at {self.viewed_at}"


class PostAnalytics(models.Model):
    """
    Daily aggregated analytics per post.

    Pre-computed from raw PostView data by the aggregate_daily_analytics task.
    """

    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="daily_analytics",
    )
    date = models.DateField(db_index=True)
    views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    avg_read_time_seconds = models.PositiveIntegerField(default=0)
    bounce_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )

    class Meta:
        db_table = "analytics_post_analytics"
        unique_together = ("post", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"Analytics for {self.post.title} on {self.date}"


class SiteAnalytics(models.Model):
    """
    Daily aggregated site-wide analytics.
    """

    date = models.DateField(unique=True, db_index=True)
    total_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    new_subscribers = models.PositiveIntegerField(default=0)
    new_posts = models.PositiveIntegerField(default=0)
    new_comments = models.PositiveIntegerField(default=0)
    top_referrers = models.JSONField(default=list, blank=True)
    top_pages = models.JSONField(default=list, blank=True)
    device_breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text='{"desktop": 60, "mobile": 35, "tablet": 5}',
    )

    class Meta:
        db_table = "analytics_site_analytics"
        ordering = ["-date"]

    def __str__(self):
        return f"Site analytics for {self.date}"
