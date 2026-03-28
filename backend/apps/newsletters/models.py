"""
Newsletter models for BlogEngine.

Manages subscribers, newsletter templates, and email campaigns.
"""

import uuid

from django.conf import settings
from django.db import models


class Subscriber(models.Model):
    """
    An email subscriber, optionally linked to a registered user.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"
        BOUNCED = "bounced", "Bounced"

    email = models.EmailField(unique=True, db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletter_subscription",
    )
    first_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "newsletters_subscriber"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    """
    A newsletter template used to compose campaigns.
    """

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    body_html = models.TextField(help_text="HTML body of the newsletter")
    body_text = models.TextField(
        blank=True, help_text="Plain text fallback"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="newsletters",
    )
    is_template = models.BooleanField(
        default=False,
        help_text="Mark as reusable template",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "newsletters_newsletter"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Campaign(models.Model):
    """
    A campaign sends a newsletter to a segment of subscribers.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    name = models.CharField(max_length=200)
    newsletter = models.ForeignKey(
        Newsletter,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    recipients = models.ManyToManyField(
        Subscriber,
        blank=True,
        related_name="campaigns",
    )
    send_to_all = models.BooleanField(
        default=True,
        help_text="Send to all active subscribers if True",
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_bounced = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "newsletters_campaign"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def open_rate(self):
        if self.total_sent == 0:
            return 0.0
        return round((self.total_opened / self.total_sent) * 100, 2)

    @property
    def click_rate(self):
        if self.total_sent == 0:
            return 0.0
        return round((self.total_clicked / self.total_sent) * 100, 2)
