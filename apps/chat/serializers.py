"""
Serializers for chat app.
"""
from rest_framework import serializers
from .models import Conversation, Message
from apps.accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'message_type', 'content',
            'media_url', 'is_read', 'read_at', 'reactions', 
            'reply_to', 'created_at'
        ]
        read_only_fields = ['conversation', 'sender', 'is_read', 'read_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message_sender = UserSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'conversation_type', 'name', 'avatar',
            'last_message', 'last_message_at', 'last_message_sender',
            'unread_count', 'created_at', 'updated_at'
        ]

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False
            ).exclude(sender=request.user).count()
        return 0
