from django.contrib import admin
from .models import Story, StoryView

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'story_type', 'views_count', 'expires_at', 'is_active']
    list_filter = ['story_type', 'is_active', 'created_at']

@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ['story', 'viewer', 'viewed_at']
