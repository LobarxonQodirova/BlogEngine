"""
Page models for BlogEngine.

Static/CMS pages (About, Contact, Custom landing pages) with template support.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class PageTemplate(models.Model):
    """
    Reusable page templates that define layout structure.

    Templates allow editors to choose a pre-built layout when creating pages.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    html_structure = models.TextField(
        help_text="HTML/component skeleton for this template",
        blank=True,
    )
    thumbnail = models.ImageField(
        upload_to="pages/templates/", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pages_template"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Page(models.Model):
    """
    A CMS-style static page.

    Supports rich content, SEO metadata, and optional template selection.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    featured_image = models.ImageField(
        upload_to="pages/images/%Y/%m/", blank=True, null=True
    )

    template = models.ForeignKey(
        PageTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pages",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    show_in_menu = models.BooleanField(default=False)
    menu_order = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pages_page"
        ordering = ["menu_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        """Build the hierarchical URL path for nested pages."""
        parts = [self.slug]
        parent = self.parent
        while parent:
            parts.insert(0, parent.slug)
            parent = parent.parent
        return "/".join(parts)
