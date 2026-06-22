"""
Views for notifications app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Notification
from .serializers import NotificationSerializer
from .tasks import mark_notifications_read


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(generics.ListAPIView):
    """Get user's notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender').order_by('-created_at')


class UnreadNotificationsCountView(generics.RetrieveAPIView):
    """Get count of unread notifications."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read."""
    mark_notifications_read.delay(request.user.id)
    return Response({"detail": "Notifications marked as read."})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark single notification as read."""
    notification = Notification.objects.filter(
        id=notification_id, recipient=request.user
    ).first()

    if notification:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({"detail": "Notification marked as read."})

    return Response(
        {"detail": "Notification not found."},
        status=status.HTTP_404_NOT_FOUND
    )
