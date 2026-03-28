"""
SEO services for BlogEngine.

Utilities for generating structured data, Open Graph tags, and XML sitemaps.
"""

import logging
from xml.etree.ElementTree import Element, SubElement, tostring

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_structured_data_for_post(post, site_url="https://blogengine.com"):
    """
    Generate Schema.org Article JSON-LD structured data for a blog post.

    Returns a dict that can be serialized directly as JSON-LD.
    """
    structured = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt or post.content[:160],
        "author": {
            "@type": "Person",
            "name": post.author.display_name,
            "url": f"{site_url}/authors/{post.author.slug}",
        },
        "datePublished": (
            post.published_at.isoformat() if post.published_at else post.created_at.isoformat()
        ),
        "dateModified": post.updated_at.isoformat(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{site_url}/posts/{post.slug}",
        },
        "wordCount": len(post.content.split()),
        "timeRequired": f"PT{post.reading_time_minutes}M",
    }

    if post.featured_image:
        structured["image"] = {
            "@type": "ImageObject",
            "url": f"{site_url}{post.featured_image.url}",
        }

    if post.category:
        structured["articleSection"] = post.category.name

    return structured


def generate_open_graph_tags(post, site_url="https://blogengine.com"):
    """
    Generate Open Graph meta tag values for a blog post.

    Returns a dict with og: prefixed keys.
    """
    tags = {
        "og:type": "article",
        "og:title": post.meta_title or post.title,
        "og:description": post.meta_description or post.excerpt or post.content[:160],
        "og:url": f"{site_url}/posts/{post.slug}",
        "og:site_name": "BlogEngine",
        "article:published_time": (
            post.published_at.isoformat() if post.published_at else ""
        ),
        "article:modified_time": post.updated_at.isoformat(),
        "article:author": post.author.display_name,
    }

    if post.featured_image:
        tags["og:image"] = f"{site_url}{post.featured_image.url}"

    if post.category:
        tags["article:section"] = post.category.name

    return tags


def generate_xml_sitemap(max_entries=50000):
    """
    Generate an XML sitemap string from published posts, pages, and
    custom Sitemap entries.

    Returns an XML string.
    """
    from apps.pages.models import Page
    from apps.posts.models import Post

    from .models import Sitemap

    root = Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Add published posts
    posts = Post.objects.filter(status="published").order_by("-published_at")[
        :max_entries
    ]
    for post in posts:
        url_el = SubElement(root, "url")
        SubElement(url_el, "loc").text = f"/posts/{post.slug}"
        if post.published_at:
            SubElement(url_el, "lastmod").text = post.published_at.strftime("%Y-%m-%d")
        SubElement(url_el, "changefreq").text = "weekly"
        SubElement(url_el, "priority").text = "0.8"

    # Add published pages
    pages = Page.objects.filter(status="published").order_by("menu_order")
    for page in pages:
        url_el = SubElement(root, "url")
        SubElement(url_el, "loc").text = f"/pages/{page.slug}"
        SubElement(url_el, "lastmod").text = page.updated_at.strftime("%Y-%m-%d")
        SubElement(url_el, "changefreq").text = "monthly"
        SubElement(url_el, "priority").text = "0.6"

    # Add custom sitemap entries
    custom_entries = Sitemap.objects.filter(is_active=True)
    for entry in custom_entries:
        url_el = SubElement(root, "url")
        SubElement(url_el, "loc").text = entry.url
        SubElement(url_el, "lastmod").text = entry.last_modified.strftime("%Y-%m-%d")
        SubElement(url_el, "changefreq").text = entry.change_frequency
        SubElement(url_el, "priority").text = str(entry.priority)

    xml_string = tostring(root, encoding="unicode", method="xml")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'


def auto_create_seo_metadata(instance, site_url="https://blogengine.com"):
    """
    Auto-create SEOMetadata for a newly published post or page
    if it doesn't already exist.
    """
    from .models import SEOMetadata

    ct = ContentType.objects.get_for_model(instance)
    seo, created = SEOMetadata.objects.get_or_create(
        content_type=ct,
        object_id=instance.pk,
        defaults={
            "meta_title": getattr(instance, "meta_title", "") or getattr(instance, "title", ""),
            "meta_description": (
                getattr(instance, "meta_description", "")
                or getattr(instance, "excerpt", "")
                or ""
            )[:160],
        },
    )

    if created:
        logger.info("Auto-created SEO metadata for %s (id=%s)", ct.model, instance.pk)

    return seo
