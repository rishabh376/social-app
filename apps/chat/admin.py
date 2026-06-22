"""
Admin configuration for chat app.
"""
from django.contrib import admin
from .models import Conversation, Message, MessageStatus


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_type', 'name', 'last_message_at', 'created_at']
    list_filter = ['conversation_type', 'created_at']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content', 'sender__username']
