"""
Celery tasks for the newsletters app.

Handles bulk email sending, scheduled campaigns, and subscriber management.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_campaign_emails(self, campaign_id):
    """
    Send emails for a campaign to all targeted subscribers.

    Processes in batches of 50 to avoid overwhelming the SMTP server.
    """
    from .models import Campaign, Subscriber

    try:
        campaign = Campaign.objects.select_related("newsletter").get(id=campaign_id)
    except Campaign.DoesNotExist:
        logger.error("Campaign %d not found.", campaign_id)
        return {"error": "Campaign not found"}

    newsletter = campaign.newsletter

    # Determine recipients
    if campaign.send_to_all:
        subscribers = Subscriber.objects.filter(status="active")
    else:
        subscribers = campaign.recipients.filter(status="active")

    total = subscribers.count()
    sent = 0
    failed = 0
    batch_size = 50

    for i in range(0, total, batch_size):
        batch = subscribers[i : i + batch_size]
        for subscriber in batch:
            try:
                personalized_html = newsletter.body_html.replace(
                    "{{first_name}}", subscriber.first_name or "Reader"
                ).replace(
                    "{{unsubscribe_url}}",
                    f"{settings.CORS_ALLOWED_ORIGINS[0]}/unsubscribe?token={subscriber.token}",
                )

                msg = EmailMultiAlternatives(
                    subject=newsletter.subject,
                    body=newsletter.body_text or "Please view in an HTML-capable client.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email],
                )
                msg.attach_alternative(personalized_html, "text/html")
                msg.send()
                sent += 1
            except Exception as e:
                failed += 1
                logger.warning(
                    "Failed to send to %s: %s", subscriber.email, str(e)
                )

    campaign.status = Campaign.Status.SENT
    campaign.sent_at = timezone.now()
    campaign.total_sent = sent
    campaign.total_bounced = failed
    campaign.save(
        update_fields=["status", "sent_at", "total_sent", "total_bounced", "updated_at"]
    )

    logger.info(
        "Campaign '%s' sent: %d delivered, %d failed out of %d.",
        campaign.name,
        sent,
        failed,
        total,
    )
    return {"sent": sent, "failed": failed, "total": total}


@shared_task
def send_scheduled_newsletters():
    """
    Check for campaigns scheduled in the past that haven't been sent yet,
    and trigger them.

    Runs every 5 minutes via Celery Beat.
    """
    from .models import Campaign

    now = timezone.now()
    scheduled = Campaign.objects.filter(
        status=Campaign.Status.SCHEDULED,
        scheduled_at__lte=now,
    )

    triggered = 0
    for campaign in scheduled:
        campaign.status = Campaign.Status.SENDING
        campaign.save(update_fields=["status"])
        send_campaign_emails.delay(campaign.id)
        triggered += 1
        logger.info("Triggered scheduled campaign: %s", campaign.name)

    return {"triggered": triggered}


@shared_task
def cleanup_bounced_subscribers(days_inactive=90):
    """
    Deactivate subscribers that have been bouncing for more than N days.
    """
    from .models import Subscriber

    cutoff = timezone.now() - timezone.timedelta(days=days_inactive)
    bounced = Subscriber.objects.filter(
        status=Subscriber.Status.BOUNCED,
        subscribed_at__lt=cutoff,
    )
    count = bounced.update(status=Subscriber.Status.UNSUBSCRIBED)
    logger.info("Deactivated %d long-bouncing subscribers.", count)
    return {"deactivated": count}
