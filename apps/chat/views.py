"""
Views for chat app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationListView(generics.ListCreateAPIView):
    """List user's conversations or create new one."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'last_message_sender')

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class ConversationDetailView(generics.RetrieveAPIView):
    """Get conversation details."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class MessageListView(generics.ListAPIView):
    """List messages in a conversation."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        conversation = get_object_or_404(
            Conversation, 
            id=self.kwargs.get('conversation_id'),
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_direct_message(request, username):
    """Start or get a direct message conversation with a user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        return Response(
            {"detail": "Cannot message yourself."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if conversation already exists
    conversation = Conversation.objects.filter(
        conversation_type='direct',
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if conversation:
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)

    # Create new conversation
    conversation = Conversation.objects.create(conversation_type='direct')
    conversation.participants.add(request.user, other_user)

    serializer = ConversationSerializer(conversation, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_conversation_read(request, conversation_id):
    """Mark all messages in conversation as read."""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    return Response({"detail": "All messages marked as read."})
