"""URL configuration for the comments app."""

from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path("", views.CommentListView.as_view(), name="comment-list"),
    path("create/", views.CommentCreateView.as_view(), name="comment-create"),
    path("<int:pk>/", views.CommentDetailView.as_view(), name="comment-detail"),
    path(
        "<int:pk>/reply/",
        views.CommentReplyCreateView.as_view(),
        name="comment-reply",
    ),
    path("<int:pk>/vote/", views.CommentVoteView.as_view(), name="comment-vote"),
    path(
        "moderation/",
        views.CommentModerationView.as_view(),
        name="comment-moderation",
    ),
]
