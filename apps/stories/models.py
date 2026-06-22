"""
Stories model (Instagram-like ephemeral content).
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Story(models.Model):
    """Ephemeral story that expires after 24 hours."""
    STORY_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='stories'
    )
    story_type = models.CharField(
        max_length=10, choices=STORY_TYPES, default='image'
    )
    media_url = models.URLField(blank=True)
    caption = models.TextField(max_length=500, blank=True)
    background_color = models.CharField(max_length=7, default='#000000')
    text_color = models.CharField(max_length=7, default='#FFFFFF')

    # Engagement
    views_count = models.PositiveIntegerField(default=0)

    # Expiration
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Story by {self.user.username}"


class StoryView(models.Model):
    """Track who viewed a story."""
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='views'
    )
    viewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='story_views'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'story_views'
        unique_together = ['story', 'viewer']
