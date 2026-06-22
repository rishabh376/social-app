"""
Chat models for real-time messaging.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Conversation(models.Model):
    """A conversation between two users (DM) or multiple users (group)."""
    CONVERSATION_TYPES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
    ]

    participants = models.ManyToManyField(
        User, related_name='conversations'
    )
    conversation_type = models.CharField(
        max_length=10, choices=CONVERSATION_TYPES, default='direct'
    )
    name = models.CharField(max_length=200, blank=True)  # For group chats
    avatar = models.ImageField(upload_to='chat_avatars/', blank=True, null=True)

    # Last message for quick preview
    last_message = models.TextField(blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='last_sent_conversations'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['-last_message_at']),
        ]

    def __str__(self):
        if self.conversation_type == 'group':
            return self.name or f"Group {self.id}"
        return f"DM: {', '.join([u.username for u in self.participants.all()])}"

    @property
    def unread_count(self, user):
        return self.messages.filter(
            is_read=False
        ).exclude(sender=user).count()


class Message(models.Model):
    """Individual chat message."""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('voice', 'Voice'),
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPES, default='text'
    )
    content = models.TextField()
    media_url = models.URLField(blank=True)

    # Message status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Reactions (emoji reactions)
    reactions = models.JSONField(default=dict, blank=True)

    # Reply to another message
    reply_to = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='replies'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username}"


class MessageStatus(models.Model):
    """Track read status per user per message."""
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='statuses'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='message_statuses'
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'message_statuses'
        unique_together = ['message', 'user']
