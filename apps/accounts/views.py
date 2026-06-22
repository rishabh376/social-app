"""
Views for accounts app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from .models import Follow
from .serializers import (
    UserSerializer, UserCreateSerializer, 
    UserUpdateSerializer, FollowSerializer
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserRegisterView(generics.CreateAPIView):
    """Register a new user."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile."""
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    """Get any user's public profile."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'


class UserSearchView(generics.ListAPIView):
    """Search users by username, name, or email."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return User.objects.none()

        cache_key = f"user_search:{query}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct()

        cache.set(cache_key, queryset, 300)  # Cache for 5 minutes
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    """Follow or unfollow a user."""
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow == request.user:
        return Response(
            {"detail": "You cannot follow yourself."},
            status=status.HTTP_400_BAD_REQUEST
        )

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    if not created:
        follow.delete()
        # Update counts
        user_to_follow.followers_count = user_to_follow.followers_set.count()
        request.user.following_count = request.user.following_set.count()
        user_to_follow.save(update_fields=['followers_count'])
        request.user.save(update_fields=['following_count'])

        return Response({
            "detail": "Unfollowed successfully.",
            "is_following": False
        })

    # Update counts
    user_to_follow.followers_count = user_to_follow.followers_set.count()
    request.user.following_count = request.user.following_set.count()
    user_to_follow.save(update_fields=['followers_count'])
    request.user.save(update_fields=['following_count'])

    # Create notification
    from apps.notifications.tasks import create_notification
    create_notification.delay(
        recipient_id=user_to_follow.id,
        sender_id=request.user.id,
        notification_type='follow'
    )

    return Response({
        "detail": "Followed successfully.",
        "is_following": True
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def followers_list(request, username):
    """Get list of followers for a user."""
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower')

    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(followers, request)
    serializer = FollowSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def following_list(request, username):
    """Get list of users a user is following."""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following')

    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(following, request)
    serializer = FollowSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def suggested_users(request):
    """Get suggested users to follow."""
    # Get users not followed by current user, excluding self
    following_ids = request.user.following_set.values_list('following_id', flat=True)

    suggested = User.objects.exclude(
        id__in=list(following_ids) + [request.user.id]
    ).order_by('-followers_count')[:10]

    serializer = UserSerializer(suggested, many=True, context={'request': request})
    return Response(serializer.data)
