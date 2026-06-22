"""
Serializers for notifications app.
"""
from rest_framework import serializers
from .models import Notification
from apps.accounts.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'message',
            'post', 'comment', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['sender', 'notification_type', 'message', 'created_at']
