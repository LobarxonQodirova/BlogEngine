"""
Comment serializers for BlogEngine.

Handles threaded comments, replies, and moderation.
"""

from rest_framework import serializers

from .models import Comment, CommentModeration, CommentReply, CommentVote


class CommentReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    author_avatar = serializers.ImageField(source="author.avatar", read_only=True)
    score = serializers.ReadOnlyField()

    class Meta:
        model = CommentReply
        fields = [
            "id",
            "comment",
            "author",
            "author_name",
            "author_avatar",
            "body",
            "is_approved",
            "is_edited",
            "upvotes",
            "downvotes",
            "score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "upvotes", "downvotes", "is_approved"]


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    author_avatar = serializers.ImageField(source="author.avatar", read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)
    reply_count = serializers.ReadOnlyField()
    score = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "author_name",
            "author_avatar",
            "body",
            "is_approved",
            "is_edited",
            "upvotes",
            "downvotes",
            "score",
            "reply_count",
            "replies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "upvotes", "downvotes", "is_approved"]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["post", "body"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ["comment", "body"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentModerationSerializer(serializers.ModelSerializer):
    moderator_name = serializers.CharField(
        source="moderator.display_name", read_only=True
    )

    class Meta:
        model = CommentModeration
        fields = [
            "id",
            "comment",
            "reply",
            "moderator",
            "moderator_name",
            "action",
            "reason",
            "created_at",
        ]
        read_only_fields = ["moderator"]


class CommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentVote
        fields = ["id", "user", "comment", "reply", "vote_type", "created_at"]
        read_only_fields = ["user"]
