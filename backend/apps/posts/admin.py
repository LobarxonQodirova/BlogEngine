"""Admin configuration for the posts app."""

from django.contrib import admin

from .models import Category, Post, PostComment, PostLike, PostView, Series, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "order", "is_active", "post_count")
    list_filter = ("is_active", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_completed", "post_count", "created_at")
    list_filter = ("is_completed",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ("author", "body", "created_at")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "is_featured",
        "view_count",
        "like_count",
        "published_at",
    )
    list_filter = ("status", "is_featured", "is_pinned", "category", "created_at")
    search_fields = ("title", "content", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author", "category", "series")
    date_hierarchy = "created_at"
    inlines = [PostCommentInline]

    fieldsets = (
        (None, {"fields": ("title", "slug", "subtitle", "content", "excerpt")}),
        (
            "Media",
            {"fields": ("featured_image", "featured_image_alt")},
        ),
        (
            "Classification",
            {"fields": ("author", "category", "series", "series_order", "custom_tags")},
        ),
        (
            "Status & Visibility",
            {"fields": ("status", "is_featured", "is_pinned", "allow_comments")},
        ),
        (
            "SEO",
            {"fields": ("meta_title", "meta_description", "canonical_url")},
        ),
        (
            "Scheduling",
            {"fields": ("published_at", "scheduled_at")},
        ),
        (
            "Stats (read-only)",
            {
                "fields": ("view_count", "like_count", "comment_count", "reading_time_minutes"),
            },
        ),
    )
    readonly_fields = ("view_count", "like_count", "comment_count", "reading_time_minutes")


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "ip_address", "viewed_at")
    list_filter = ("viewed_at",)
    raw_id_fields = ("post", "user")
    date_hierarchy = "viewed_at"


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    raw_id_fields = ("post", "user")


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    raw_id_fields = ("post", "author")
