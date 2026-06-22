"""
Admin configuration for posts app.
"""
from django.contrib import admin
from .models import Post, Comment, Like, SavedPost, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post_type', 'likes_count', 
                    'comments_count', 'created_at']
    list_filter = ['post_type', 'created_at', 'is_archived']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'likes_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'like_type', 'post', 'comment', 'created_at']
    list_filter = ['like_type', 'created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'posts_count', 'created_at']
    search_fields = ['name']
