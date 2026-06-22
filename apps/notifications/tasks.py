"""
Celery tasks for notifications.
"""
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


@shared_task
def create_notification(recipient_id, sender_id, notification_type, post_id=None, comment_id=None):
    """Create notification and send real-time alert via WebSocket."""
    try:
        recipient = User.objects.get(id=recipient_id)
        sender = User.objects.get(id=sender_id)

        # Don't notify if sender is recipient
        if recipient_id == sender_id:
            return

        # Build message
        messages = {
            'like': f'{sender.username} liked your post',
            'comment': f'{sender.username} commented on your post',
            'follow': f'{sender.username} started following you',
            'message': f'{sender.username} sent you a message',
            'mention': f'{sender.username} mentioned you',
            'story_view': f'{sender.username} viewed your story',
            'post_share': f'{sender.username} shared your post',
        }

        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            post_id=post_id,
            comment_id=comment_id,
            message=messages.get(notification_type, 'New notification')
        )

        # Send real-time notification via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient_id}",
            {
                'type': 'notification',
                'notification_type': notification_type,
                'data': {
                    'id': notification.id,
                    'sender': {
                        'id': sender.id,
                        'username': sender.username,
                        'avatar': sender.avatar.url if sender.avatar else None
                    },
                    'type': notification_type,
                    'message': notification.message,
                    'post_id': post_id,
                    'created_at': notification.created_at.isoformat(),
                    'is_read': False
                }
            }
        )

        return notification.id
    except User.DoesNotExist:
        return None


@shared_task
def mark_notifications_read(user_id):
    """Mark all notifications as read for a user."""
    Notification.objects.filter(
        recipient_id=user_id, is_read=False
    ).update(is_read=True)
