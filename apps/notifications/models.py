"""
Notification models for real-time alerts.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """User notification for likes, comments, follows, messages."""
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('message', 'Message'),
        ('mention', 'Mention'),
        ('story_view', 'Story View'),
        ('post_share', 'Post Share'),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES)

    # Related content
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        'posts.Comment', on_delete=models.CASCADE, null=True, blank=True
    )

    # Content
    message = models.CharField(max_length=300, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.notification_type} to {self.recipient.username}"
