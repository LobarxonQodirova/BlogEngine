"""
Comment models for BlogEngine.

Full threaded comment system with moderation and voting.
"""

from django.conf import settings
from django.db import models


class Comment(models.Model):
    """
    Top-level comment on a blog post.

    Supports threaded replies via the CommentReply model.
    """

    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="threaded_comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField(max_length=5000)
    is_approved = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments_comment"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def score(self):
        return self.upvotes - self.downvotes


class CommentReply(models.Model):
    """
    A reply to a top-level comment, creating a threaded structure.
    """

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_replies",
    )
    body = models.TextField(max_length=3000)
    is_approved = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments_reply"
        ordering = ["created_at"]
        verbose_name_plural = "comment replies"

    def __str__(self):
        return f"Reply by {self.author.username} to comment #{self.comment.id}"

    @property
    def score(self):
        return self.upvotes - self.downvotes


class CommentModeration(models.Model):
    """
    Tracks moderation actions taken on comments and replies.
    """

    class Action(models.TextChoices):
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"
        FLAG = "flag", "Flag"
        SPAM = "spam", "Spam"
        DELETE = "delete", "Delete"

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="moderation_log",
    )
    reply = models.ForeignKey(
        CommentReply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="moderation_log",
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="moderation_actions",
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments_moderation"
        ordering = ["-created_at"]

    def __str__(self):
        target = self.comment or self.reply
        return f"{self.action} on {target} by {self.moderator}"


class CommentVote(models.Model):
    """
    Records user votes on comments to prevent duplicate voting.
    """

    class VoteType(models.TextChoices):
        UP = "up", "Upvote"
        DOWN = "down", "Downvote"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_votes",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )
    reply = models.ForeignKey(
        CommentReply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )
    vote_type = models.CharField(max_length=4, choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments_vote"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                condition=models.Q(comment__isnull=False),
                name="unique_comment_vote",
            ),
            models.UniqueConstraint(
                fields=["user", "reply"],
                condition=models.Q(reply__isnull=False),
                name="unique_reply_vote",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} {self.vote_type} vote"
