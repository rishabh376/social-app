"""
WebSocket consumers for real-time chat.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer handling real-time chat over WebSocket."""

    async def connect(self):
        """Accept connection and join user's personal notification group."""
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Personal notification group for this user
        self.user_group_name = f"user_{self.user.id}"

        # Join user's personal group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Update online status
        await self.set_user_online(True)

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected as {self.user.username}'
        }))

    async def disconnect(self, close_code):
        """Leave groups and set offline."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

            # Leave conversation group if joined
            if hasattr(self, 'conversation_group_name'):
                await self.channel_layer.group_discard(
                    self.conversation_group_name,
                    self.channel_name
                )

            await self.set_user_online(False)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'join_conversation':
                await self.join_conversation(data)
            elif message_type == 'leave_conversation':
                await self.leave_conversation(data)
            elif message_type == 'send_message':
                await self.handle_send_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_message':
                await self.handle_read_message(data)
            elif message_type == 'reaction':
                await self.handle_reaction(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def join_conversation(self, data):
        """Join a conversation room."""
        conversation_id = data.get('conversation_id')

        # Verify user is participant
        is_participant = await self.check_conversation_access(
            conversation_id, self.user.id
        )

        if not is_participant:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Not authorized for this conversation'
            }))
            return

        # Leave previous conversation if any
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )

        self.conversation_id = conversation_id
        self.conversation_group_name = f"conversation_{conversation_id}"

        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        # Load recent messages
        messages = await self.get_conversation_messages(conversation_id)

        await self.send(text_data=json.dumps({
            'type': 'conversation_joined',
            'conversation_id': conversation_id,
            'messages': messages
        }))

    async def leave_conversation(self, data):
        """Leave current conversation."""
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
            delattr(self, 'conversation_group_name')
            delattr(self, 'conversation_id')

        await self.send(text_data=json.dumps({
            'type': 'conversation_left'
        }))

    async def handle_send_message(self, data):
        """Handle sending a new message."""
        conversation_id = data.get('conversation_id')
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        reply_to_id = data.get('reply_to')

        if not content:
            return

        # Save message to database
        message = await self.save_message(
            conversation_id, self.user.id, content, message_type, reply_to_id
        )

        if not message:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to save message'
            }))
            return

        # Broadcast to conversation group
        await self.channel_layer.group_send(
            f"conversation_{conversation_id}",
            {
                'type': 'chat_message',
                'message': message
            }
        )

        # Send notification to other participants
        participants = await self.get_conversation_participants(conversation_id)
        for participant_id in participants:
            if participant_id != self.user.id:
                await self.channel_layer.group_send(
                    f"user_{participant_id}",
                    {
                        'type': 'new_message_notification',
                        'message': {
                            'conversation_id': conversation_id,
                            'sender': self.user.username,
                            'content': content[:100],
                            'timestamp': message['created_at']
                        }
                    }
                )

    async def handle_typing(self, data):
        """Broadcast typing indicator."""
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', True)

        await self.channel_layer.group_send(
            f"conversation_{conversation_id}",
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    async def handle_read_message(self, data):
        """Mark message as read."""
        message_id = data.get('message_id')
        await self.mark_message_read(message_id, self.user.id)

        # Notify sender
        message = await self.get_message_sender(message_id)
        if message:
            await self.channel_layer.group_send(
                f"user_{message['sender_id']}",
                {
                    'type': 'message_read',
                    'message_id': message_id,
                    'read_by': self.user.id
                }
            )

    async def handle_reaction(self, data):
        """Handle message reaction."""
        message_id = data.get('message_id')
        emoji = data.get('emoji')

        await self.add_reaction(message_id, self.user.id, emoji)

        # Broadcast reaction
        conversation_id = data.get('conversation_id')
        await self.channel_layer.group_send(
            f"conversation_{conversation_id}",
            {
                'type': 'message_reaction',
                'message_id': message_id,
                'user_id': self.user.id,
                'emoji': emoji
            }
        )

    # ─── Message Handlers (receive from channel layer) ───

    async def chat_message(self, event):
        """Receive message from conversation group."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))

    async def typing_indicator(self, event):
        """Receive typing indicator."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    async def new_message_notification(self, event):
        """Receive new message notification."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': 'new_message',
            'data': event['message']
        }))

    async def message_read(self, event):
        """Receive read receipt."""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'read_by': event['read_by']
        }))

    async def message_reaction(self, event):
        """Receive reaction update."""
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'emoji': event['emoji']
        }))

    # ─── Database Operations (sync_to_async) ───

    @database_sync_to_async
    def set_user_online(self, is_online):
        """Update user's online status."""
        self.user.is_online = is_online
        self.user.save(update_fields=['is_online'])

    @database_sync_to_async
    def check_conversation_access(self, conversation_id, user_id):
        """Check if user is a participant."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation.participants.filter(id=user_id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def get_conversation_messages(self, conversation_id, limit=50):
        """Get recent messages for a conversation."""
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender').order_by('-created_at')[:limit]

        return [{
            'id': msg.id,
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username,
                'avatar': msg.sender.avatar.url if msg.sender.avatar else None
            },
            'content': msg.content,
            'message_type': msg.message_type,
            'is_read': msg.is_read,
            'reactions': msg.reactions,
            'created_at': msg.created_at.isoformat()
        } for msg in reversed(messages)]

    @database_sync_to_async
    def save_message(self, conversation_id, sender_id, content, msg_type, reply_to_id):
        """Save message to database."""
        try:
            message = Message.objects.create(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                message_type=msg_type,
                reply_to_id=reply_to_id
            )

            # Update conversation last message
            conversation = Conversation.objects.get(id=conversation_id)
            conversation.last_message = content[:200]
            conversation.last_message_at = message.created_at
            conversation.last_message_sender_id = sender_id
            conversation.save()

            return {
                'id': message.id,
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username,
                    'avatar': message.sender.avatar.url if message.sender.avatar else None
                },
                'content': message.content,
                'message_type': message.message_type,
                'is_read': message.is_read,
                'reactions': message.reactions,
                'created_at': message.created_at.isoformat()
            }
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def get_conversation_participants(self, conversation_id):
        """Get participant IDs."""
        conversation = Conversation.objects.get(id=conversation_id)
        return list(conversation.participants.values_list('id', flat=True))

    @database_sync_to_async
    def mark_message_read(self, message_id, user_id):
        """Mark message as read."""
        try:
            message = Message.objects.get(id=message_id)
            if message.sender_id != user_id:
                message.is_read = True
                message.save(update_fields=['is_read'])
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def get_message_sender(self, message_id):
        """Get message sender ID."""
        try:
            message = Message.objects.get(id=message_id)
            return {'sender_id': message.sender_id}
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def add_reaction(self, message_id, user_id, emoji):
        """Add reaction to message."""
        try:
            message = Message.objects.get(id=message_id)
            reactions = message.reactions or {}
            if emoji not in reactions:
                reactions[emoji] = []
            if user_id not in reactions[emoji]:
                reactions[emoji].append(user_id)
            message.reactions = reactions
            message.save(update_fields=['reactions'])
        except Message.DoesNotExist:
            pass
