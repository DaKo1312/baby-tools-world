from django.contrib import admin

from .models import Category, Comment, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Make the Tag model available in the Django admin panel."""

    list_display = ("name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "average_rating", "rating_count", "created_at")
    list_filter = ("tags",)
    list_select_related = ("category",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "guest_name", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("guest_name", "guest_email", "text", "user__username")
