"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 
                    'is_verified', 'is_online', 'followers_count', 'date_joined']
    list_filter = ['is_verified', 'is_online', 'is_private', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar', 'cover_photo', 'phone')}),
        ('Stats', {'fields': ('followers_count', 'following_count', 'posts_count')}),
        ('Privacy', {'fields': ('is_private', 'is_verified', 'is_online')}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
