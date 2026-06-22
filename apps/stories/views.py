from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Story, StoryView
from .serializers import StorySerializer, StoryViewSerializer


class ActiveStoriesView(generics.ListAPIView):
    """Get active stories from followed users."""
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        following_ids = self.request.user.following_set.values_list(
            'following_id', flat=True
        )
        return Story.objects.filter(
            user__in=following_ids,
            is_active=True,
            expires_at__gt=timezone.now()
        ).select_related('user')


class MyStoriesView(generics.ListCreateAPIView):
    """Get or create user's own stories."""
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        from datetime import timedelta
        expires = timezone.now() + timedelta(hours=24)
        serializer.save(user=self.request.user, expires_at=expires)


class ViewStoryView(generics.CreateAPIView):
    """Mark a story as viewed."""
    serializer_class = StoryViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        story = get_object_or_404(
            Story, id=self.kwargs.get('story_id'),
            is_active=True, expires_at__gt=timezone.now()
        )

        view, created = StoryView.objects.get_or_create(
            story=story,
            viewer=self.request.user
        )

        if created:
            story.views_count = StoryView.objects.filter(story=story).count()
            story.save(update_fields=['views_count'])

        return view
