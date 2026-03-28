"""
Newsletter views for BlogEngine.

Handles subscription, campaign management, and newsletter CRUD.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser, IsEditor

from .models import Campaign, Newsletter, Subscriber
from .serializers import (
    CampaignSendSerializer,
    CampaignSerializer,
    NewsletterSerializer,
    SubscribeSerializer,
    SubscriberSerializer,
    UnsubscribeSerializer,
)
from .tasks import send_campaign_emails


class SubscribeView(APIView):
    """
    POST /api/newsletters/subscribe/
    Public endpoint for newsletter subscription.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubscribeSerializer(
            data=request.data,
            context={"ip_address": request.META.get("REMOTE_ADDR")},
        )
        serializer.is_valid(raise_exception=True)
        subscriber = serializer.save()
        return Response(
            {
                "detail": "Successfully subscribed!",
                "email": subscriber.email,
            },
            status=status.HTTP_201_CREATED,
        )


class UnsubscribeView(APIView):
    """
    POST /api/newsletters/unsubscribe/
    Unsubscribe via email or unique token.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        token = serializer.validated_data.get("token")

        try:
            if token:
                subscriber = Subscriber.objects.get(token=token)
            else:
                subscriber = Subscriber.objects.get(email=email)

            subscriber.status = Subscriber.Status.UNSUBSCRIBED
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save(update_fields=["status", "unsubscribed_at"])

            return Response({"detail": "Successfully unsubscribed."})
        except Subscriber.DoesNotExist:
            return Response(
                {"detail": "Subscriber not found."}, status=status.HTTP_404_NOT_FOUND
            )


class SubscriberListView(generics.ListAPIView):
    """
    GET /api/newsletters/subscribers/
    Admin-only: list all subscribers with filtering.
    """

    serializer_class = SubscriberSerializer
    permission_classes = [IsAdminUser]
    queryset = Subscriber.objects.all()
    filterset_fields = ["status", "confirmed"]
    search_fields = ["email", "first_name"]


class NewsletterViewSet(viewsets.ModelViewSet):
    """CRUD for newsletter templates/content."""

    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsEditor]
    search_fields = ["title", "subject"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CampaignViewSet(viewsets.ModelViewSet):
    """CRUD for email campaigns."""

    queryset = Campaign.objects.select_related("newsletter").all()
    serializer_class = CampaignSerializer
    permission_classes = [IsEditor]
    filterset_fields = ["status"]


class CampaignSendView(APIView):
    """
    POST /api/newsletters/campaigns/send/
    Trigger sending a campaign to its subscribers.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CampaignSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        campaign_id = serializer.validated_data["campaign_id"]
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response(
                {"detail": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if campaign.status in ("sending", "sent"):
            return Response(
                {"detail": f"Campaign is already {campaign.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign.status = Campaign.Status.SENDING
        campaign.save(update_fields=["status"])

        # Dispatch async
        send_campaign_emails.delay(campaign_id)

        return Response(
            {
                "detail": "Campaign sending started.",
                "campaign_id": campaign_id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
