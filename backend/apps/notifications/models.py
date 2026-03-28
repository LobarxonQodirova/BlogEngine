"""
Notification models for BlogEngine.

In-app notification system for comments, likes, mentions, and admin alerts.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Notification(models.Model):
    """
    A notification addressed to a specific user.

    Uses generic relations so any model can trigger a notification.
    """

    class NotificationType(models.TextChoices):
        COMMENT = "comment", "New Comment"
        REPLY = "reply", "Comment Reply"
        LIKE = "like", "Post Like"
        MENTION = "mention", "Mention"
        FOLLOW = "follow", "New Follower"
        PUBLISH = "publish", "Post Published"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NotificationType.choices,
    )
    title = models.CharField(max_length=200)
    message = models.TextField(max_length=500, blank=True)
    url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Frontend URL to link to when notification is clicked",
    )

    # Generic relation to the triggering object (post, comment, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notifications_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title} -> {self.recipient.username}"

    def mark_as_read(self):
        from django.utils import timezone

        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
