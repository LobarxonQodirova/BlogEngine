"""
Notification services for BlogEngine.

High-level helpers for querying, marking, and managing notifications.
"""

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


def get_unread_count(user):
    """Return the count of unread notifications for a user."""
    return Notification.objects.filter(
        recipient=user, is_read=False
    ).count()


def get_recent_notifications(user, limit=20):
    """
    Return the most recent notifications for a user.

    Includes both read and unread, ordered by creation time.
    """
    return Notification.objects.filter(
        recipient=user
    ).select_related("sender")[:limit]


def mark_all_as_read(user):
    """
    Mark all unread notifications for a user as read.

    Returns the number of notifications marked.
    """
    now = timezone.now()
    count = Notification.objects.filter(
        recipient=user, is_read=False
    ).update(is_read=True, read_at=now)
    logger.info("Marked %d notifications as read for user %s.", count, user.username)
    return count


def mark_notification_read(notification_id, user):
    """
    Mark a single notification as read.

    Returns True if successful, False if not found or not the recipient.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id, recipient=user
        )
        notification.mark_as_read()
        return True
    except Notification.DoesNotExist:
        return False


def create_system_notification(recipient_id, title, message="", url=""):
    """
    Create a system-level notification (e.g., maintenance, announcements).
    """
    return Notification.objects.create(
        recipient_id=recipient_id,
        notification_type=Notification.NotificationType.SYSTEM,
        title=title,
        message=message,
        url=url,
    )


def broadcast_system_notification(title, message="", url=""):
    """
    Send a system notification to all active users.

    Returns the count of notifications created.
    """
    active_users = User.objects.filter(is_active=True).values_list("id", flat=True)
    notifications = [
        Notification(
            recipient_id=uid,
            notification_type=Notification.NotificationType.SYSTEM,
            title=title,
            message=message,
            url=url,
        )
        for uid in active_users
    ]
    created = Notification.objects.bulk_create(notifications)
    logger.info("Broadcast system notification to %d users.", len(created))
    return len(created)


def get_notification_preferences(user):
    """
    Return notification preference settings for a user.

    This is a stub that could be expanded with a UserPreferences model.
    """
    return {
        "email_on_comment": True,
        "email_on_like": False,
        "email_on_mention": True,
        "email_on_follow": True,
        "email_on_system": True,
    }
