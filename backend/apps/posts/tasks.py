"""
Celery tasks for the posts app.

Handles scheduled publishing, revision cleanup, and post-processing.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def publish_scheduled_posts(self):
    """
    Publish all posts whose scheduled_at time has passed.

    Runs every minute via Celery Beat.
    """
    from .models import Post

    now = timezone.now()
    scheduled_posts = Post.objects.filter(
        status=Post.Status.SCHEDULED,
        scheduled_at__lte=now,
    )

    count = 0
    for post in scheduled_posts:
        post.status = Post.Status.PUBLISHED
        post.published_at = now
        post.save(update_fields=["status", "published_at", "updated_at"])
        count += 1
        logger.info("Published scheduled post: %s (id=%d)", post.title, post.id)

    if count:
        logger.info("Published %d scheduled posts.", count)
    return {"published": count}


@shared_task(bind=True, max_retries=2)
def cleanup_old_revisions(self):
    """
    Remove post view records older than 90 days to keep the database lean.

    Runs weekly via Celery Beat.
    """
    from .models import PostView

    cutoff = timezone.now() - timezone.timedelta(days=90)
    deleted_count, _ = PostView.objects.filter(viewed_at__lt=cutoff).delete()
    logger.info("Cleaned up %d old post view records.", deleted_count)
    return {"deleted": deleted_count}


@shared_task
def update_post_stats(post_id):
    """
    Recalculate and update aggregated stats for a single post.
    Called after significant events (bulk import, data correction).
    """
    from .models import Post, PostComment, PostLike, PostView

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        logger.warning("Post %d not found for stats update.", post_id)
        return

    post.view_count = PostView.objects.filter(post=post).count()
    post.like_count = PostLike.objects.filter(post=post).count()
    post.comment_count = PostComment.objects.filter(post=post, is_approved=True).count()
    post.save(update_fields=["view_count", "like_count", "comment_count"])
    logger.info("Updated stats for post: %s", post.title)


@shared_task
def generate_post_excerpt(post_id):
    """
    Auto-generate an excerpt from the post content if none was provided.
    """
    from .models import Post

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return

    if not post.excerpt and post.content:
        # Strip markdown-like syntax for a clean excerpt
        import re

        clean = re.sub(r"[#*_\[\]()>`~]", "", post.content)
        clean = re.sub(r"\s+", " ", clean).strip()
        post.excerpt = clean[:480]
        post.save(update_fields=["excerpt"])
        logger.info("Generated excerpt for post: %s", post.title)
