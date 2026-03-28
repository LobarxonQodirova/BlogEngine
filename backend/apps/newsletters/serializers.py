"""
Newsletter serializers for BlogEngine.

Handles Subscriber, Newsletter, and Campaign serialization.
"""

from rest_framework import serializers

from .models import Campaign, Newsletter, Subscriber


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = [
            "id",
            "email",
            "first_name",
            "status",
            "confirmed",
            "subscribed_at",
            "unsubscribed_at",
        ]
        read_only_fields = ["status", "confirmed", "subscribed_at", "unsubscribed_at"]


class SubscribeSerializer(serializers.Serializer):
    """Public serializer for newsletter subscription."""

    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=False, default="")

    def validate_email(self, value):
        if Subscriber.objects.filter(email=value, status="active").exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value

    def create(self, validated_data):
        subscriber, created = Subscriber.objects.update_or_create(
            email=validated_data["email"],
            defaults={
                "first_name": validated_data.get("first_name", ""),
                "status": Subscriber.Status.ACTIVE,
                "unsubscribed_at": None,
                "ip_address": self.context.get("ip_address"),
            },
        )
        return subscriber


class UnsubscribeSerializer(serializers.Serializer):
    """Serializer for unsubscribing via email or token."""

    email = serializers.EmailField(required=False)
    token = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("token"):
            raise serializers.ValidationError(
                "Either email or token must be provided."
            )
        return attrs


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "subject",
            "body_html",
            "body_text",
            "author",
            "is_template",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author"]


class CampaignSerializer(serializers.ModelSerializer):
    newsletter_title = serializers.CharField(
        source="newsletter.title", read_only=True
    )
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "newsletter",
            "newsletter_title",
            "status",
            "send_to_all",
            "scheduled_at",
            "sent_at",
            "total_sent",
            "total_opened",
            "total_clicked",
            "total_bounced",
            "open_rate",
            "click_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "sent_at",
            "total_sent",
            "total_opened",
            "total_clicked",
            "total_bounced",
        ]


class CampaignSendSerializer(serializers.Serializer):
    """Trigger sending for a specific campaign."""

    campaign_id = serializers.IntegerField(required=True)
