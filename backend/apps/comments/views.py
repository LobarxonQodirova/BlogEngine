"""
Comment views for BlogEngine.

Handles threaded comments with voting and moderation.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsEditor, IsOwnerOrReadOnly

from .models import Comment, CommentModeration, CommentReply, CommentVote
from .serializers import (
    CommentCreateSerializer,
    CommentModerationSerializer,
    CommentReplyCreateSerializer,
    CommentReplySerializer,
    CommentSerializer,
    CommentVoteSerializer,
)


class CommentListView(generics.ListAPIView):
    """
    GET /api/comments/?post=<id>
    List approved comments for a post with threaded replies.
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Comment.objects.filter(is_approved=True).select_related(
            "author"
        ).prefetch_related("replies__author")
        post_id = self.request.query_params.get("post")
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs


class CommentCreateView(generics.CreateAPIView):
    """
    POST /api/comments/
    Create a new top-level comment.
    """

    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/comments/<id>/
    Retrieve, update, or delete a comment. Only the author can modify.
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Comment.objects.all()

    def perform_update(self, serializer):
        serializer.save(is_edited=True)


class CommentReplyCreateView(generics.CreateAPIView):
    """
    POST /api/comments/<id>/reply/
    Reply to a specific comment.
    """

    serializer_class = CommentReplyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        comment = Comment.objects.get(pk=self.kwargs["pk"])
        serializer.save(comment=comment)


class CommentVoteView(APIView):
    """
    POST /api/comments/<id>/vote/
    Vote (upvote or downvote) on a comment.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        vote_type = request.data.get("vote_type", "up")
        if vote_type not in ("up", "down"):
            return Response(
                {"detail": "vote_type must be 'up' or 'down'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=404)

        existing = CommentVote.objects.filter(
            user=request.user, comment=comment
        ).first()

        if existing:
            if existing.vote_type == vote_type:
                # Undo the vote
                if vote_type == "up":
                    comment.upvotes = max(0, comment.upvotes - 1)
                else:
                    comment.downvotes = max(0, comment.downvotes - 1)
                comment.save(update_fields=["upvotes", "downvotes"])
                existing.delete()
                return Response({"detail": "Vote removed.", "score": comment.score})
            else:
                # Switch vote
                if vote_type == "up":
                    comment.upvotes += 1
                    comment.downvotes = max(0, comment.downvotes - 1)
                else:
                    comment.downvotes += 1
                    comment.upvotes = max(0, comment.upvotes - 1)
                existing.vote_type = vote_type
                existing.save()
                comment.save(update_fields=["upvotes", "downvotes"])
                return Response({"detail": "Vote changed.", "score": comment.score})
        else:
            CommentVote.objects.create(
                user=request.user, comment=comment, vote_type=vote_type
            )
            if vote_type == "up":
                comment.upvotes += 1
            else:
                comment.downvotes += 1
            comment.save(update_fields=["upvotes", "downvotes"])
            return Response({"detail": "Vote recorded.", "score": comment.score})


class CommentModerationView(generics.ListCreateAPIView):
    """
    GET  /api/comments/moderation/ - list moderation log (editors only)
    POST /api/comments/moderation/ - perform a moderation action
    """

    serializer_class = CommentModerationSerializer
    permission_classes = [IsEditor]
    queryset = CommentModeration.objects.select_related(
        "moderator", "comment", "reply"
    ).all()

    def perform_create(self, serializer):
        mod = serializer.save(moderator=self.request.user)

        # Apply the moderation action
        target = mod.comment or mod.reply
        if target and mod.action in ("approve",):
            target.is_approved = True
            target.save(update_fields=["is_approved"])
        elif target and mod.action in ("reject", "spam", "delete"):
            target.is_approved = False
            target.save(update_fields=["is_approved"])
