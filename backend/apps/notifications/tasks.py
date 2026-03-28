"""
Celery tasks for the notifications app.

Handles async notification creation, email notification delivery, and cleanup.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def create_notification(
    recipient_id,
    notification_type,
    title,
    message="",
    url="",
    sender_id=None,
    content_type_id=None,
    object_id=None,
):
    """
    Create a notification record asynchronously.

    This is the main entry point for all notification creation.
    """
    from .models import Notification

    notification = Notification.objects.create(
        recipient_id=recipient_id,
        sender_id=sender_id,
        notification_type=notification_type,
        title=title,
        message=message,
        url=url,
        content_type_id=content_type_id,
        object_id=object_id,
    )
    logger.info(
        "Created notification %d (%s) for user %d",
        notification.id,
        notification_type,
        recipient_id,
    )
    return notification.id


@shared_task
def send_notification_email(notification_id):
    """
    Send an email for a specific notification if the user has email enabled.
    """
    from django.contrib.auth import get_user_model

    from .models import Notification

    User = get_user_model()

    try:
        notification = Notification.objects.select_related("recipient").get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.warning("Notification %d not found for email.", notification_id)
        return

    recipient = notification.recipient
    if not recipient.email_verified:
        return

    try:
        send_mail(
            subject=f"BlogEngine: {notification.title}",
            message=notification.message or notification.title,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info("Sent notification email to %s.", recipient.email)
    except Exception as e:
        logger.error("Failed to send notification email: %s", str(e))


@shared_task
def notify_comment_on_post(comment_id):
    """
    Notify the post author when someone comments on their post.
    """
    from apps.comments.models import Comment

    try:
        comment = Comment.objects.select_related("post__author", "author").get(
            id=comment_id
        )
    except Comment.DoesNotExist:
        return

    post = comment.post
    if comment.author == post.author:
        return  # Don't notify yourself

    create_notification.delay(
        recipient_id=post.author.id,
        sender_id=comment.author.id,
        notification_type="comment",
        title=f"New comment on \"{post.title}\"",
        message=f"{comment.author.display_name} commented: {comment.body[:100]}",
        url=f"/posts/{post.slug}#comment-{comment.id}",
    )


@shared_task
def notify_post_liked(post_id, liker_id):
    """
    Notify the post author when someone likes their post.
    """
    from apps.posts.models import Post

    try:
        post = Post.objects.select_related("author").get(id=post_id)
    except Post.DoesNotExist:
        return

    if liker_id == post.author.id:
        return

    from django.contrib.auth import get_user_model

    User = get_user_model()
    liker = User.objects.get(id=liker_id)

    create_notification.delay(
        recipient_id=post.author.id,
        sender_id=liker_id,
        notification_type="like",
        title=f"{liker.display_name} liked your post",
        message=f'Your post "{post.title}" received a like!',
        url=f"/posts/{post.slug}",
    )


@shared_task
def cleanup_old_notifications(days=90):
    """
    Remove read notifications older than N days.
    """
    from .models import Notification

    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count, _ = Notification.objects.filter(
        is_read=True, created_at__lt=cutoff
    ).delete()
    logger.info("Cleaned up %d old notifications.", deleted_count)
    return {"deleted": deleted_count}
