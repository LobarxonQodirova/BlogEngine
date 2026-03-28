"""
SEO models for BlogEngine.

Manages SEO metadata, Open Graph tags, structured data, and sitemap entries.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SEOMetadata(models.Model):
    """
    Stores SEO metadata that can be attached to any model (Post, Page, etc.)
    via Django's generic relations.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)

    # Open Graph
    og_title = models.CharField(max_length=95, blank=True)
    og_description = models.CharField(max_length=200, blank=True)
    og_image = models.URLField(blank=True)
    og_type = models.CharField(max_length=30, default="article", blank=True)

    # Twitter Card
    twitter_card = models.CharField(
        max_length=20,
        default="summary_large_image",
        choices=[
            ("summary", "Summary"),
            ("summary_large_image", "Summary Large Image"),
        ],
    )
    twitter_title = models.CharField(max_length=70, blank=True)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_image = models.URLField(blank=True)

    # Schema.org structured data (JSON-LD)
    structured_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON-LD structured data for this content",
    )

    no_index = models.BooleanField(default=False)
    no_follow = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "seo_metadata"
        unique_together = ("content_type", "object_id")
        verbose_name = "SEO metadata"
        verbose_name_plural = "SEO metadata"

    def __str__(self):
        return f"SEO: {self.meta_title or self.content_object}"

    @property
    def robots_directives(self):
        """Build the robots meta tag content."""
        directives = []
        if self.no_index:
            directives.append("noindex")
        if self.no_follow:
            directives.append("nofollow")
        return ", ".join(directives) if directives else "index, follow"


class Sitemap(models.Model):
    """
    Manually managed sitemap entries for pages that need custom priority
    or change frequency overrides.
    """

    class ChangeFrequency(models.TextChoices):
        ALWAYS = "always", "Always"
        HOURLY = "hourly", "Hourly"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"
        NEVER = "never", "Never"

    url = models.URLField(unique=True)
    title = models.CharField(max_length=200, blank=True)
    priority = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.5,
        help_text="Priority from 0.0 to 1.0",
    )
    change_frequency = models.CharField(
        max_length=10,
        choices=ChangeFrequency.choices,
        default=ChangeFrequency.WEEKLY,
    )
    last_modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seo_sitemap"
        ordering = ["-priority", "url"]

    def __str__(self):
        return self.url
