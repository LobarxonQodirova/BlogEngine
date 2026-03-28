"""URL configuration for the accounts app."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", views.TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "author-profile/",
        views.AuthorProfileView.as_view(),
        name="author-profile",
    ),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path("authors/", views.AuthorListView.as_view(), name="author-list"),
    path(
        "authors/<slug:slug>/",
        views.AuthorDetailView.as_view(),
        name="author-detail",
    ),
    path("users/", views.UserManagementView.as_view(), name="user-management"),
]
