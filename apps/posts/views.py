"""
Views for posts app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.core.cache import cache
from .models import Post, Comment, Like, SavedPost, Tag
from .serializers import (
    PostSerializer, PostCreateSerializer, 
    CommentSerializer, TagSerializer
)
from apps.notifications.tasks import create_notification


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class FeedView(generics.ListAPIView):
    """Get personalized feed (posts from followed users)."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        cache_key = f"feed:{user.id}"
        cached = cache.get(cache_key)

        if cached is not None:
            return cached

        # Get posts from followed users + own posts
        following_ids = user.following_set.values_list('following_id', flat=True)
        queryset = Post.objects.filter(
            Q(author__in=following_ids) | Q(author=user)
        ).select_related('author').prefetch_related('comments', 'likes', 'saves')

        cache.set(cache_key, queryset, 60)  # Cache for 1 minute
        return queryset


class PostListCreateView(generics.ListCreateAPIView):
    """List all posts or create new post."""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def get_queryset(self):
        return Post.objects.all().select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific post."""
    queryset = Post.objects.all().select_related('author')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.IsAuthenticated()]


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class CommentListCreateView(generics.ListCreateAPIView):
    """List comments on a post or add new comment."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(
            post_id=post_id, parent__isnull=True
        ).select_related('author').prefetch_related('replies')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        comment = serializer.save(author=self.request.user, post=post)

        # Update post comments count
        post.comments_count = Comment.objects.filter(post=post).count()
        post.save(update_fields=['comments_count'])

        # Notify post author
        if post.author != self.request.user:
            create_notification.delay(
                recipient_id=post.author.id,
                sender_id=self.request.user.id,
                notification_type='comment',
                post_id=post.id
            )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    """Like or unlike a post."""
    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        like_type='post',
        post=post
    )

    if not created:
        like.delete()
        post.likes_count = post.likes.count()
        post.save(update_fields=['likes_count'])
        return Response({"detail": "Unliked.", "is_liked": False})

    post.likes_count = post.likes.count()
    post.save(update_fields=['likes_count'])

    # Notify post author
    if post.author != request.user:
        create_notification.delay(
            recipient_id=post.author.id,
            sender_id=request.user.id,
            notification_type='like',
            post_id=post.id
        )

    return Response({"detail": "Liked.", "is_liked": True}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_comment(request, comment_id):
    """Like or unlike a comment."""
    comment = get_object_or_404(Comment, id=comment_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        like_type='comment',
        comment=comment
    )

    if not created:
        like.delete()
        comment.likes_count = comment.likes.count()
        comment.save(update_fields=['likes_count'])
        return Response({"detail": "Unliked.", "is_liked": False})

    comment.likes_count = comment.likes.count()
    comment.save(update_fields=['likes_count'])
    return Response({"detail": "Liked.", "is_liked": True}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_post(request, post_id):
    """Save or unsave a post."""
    post = get_object_or_404(Post, id=post_id)

    saved, created = SavedPost.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        saved.delete()
        post.saves_count = post.saves.count()
        post.save(update_fields=['saves_count'])
        return Response({"detail": "Removed from saved.", "is_saved": False})

    post.saves_count = post.saves.count()
    post.save(update_fields=['saves_count'])
    return Response({"detail": "Saved.", "is_saved": True}, status=status.HTTP_201_CREATED)


class TrendingPostsView(generics.ListAPIView):
    """Get trending posts based on engagement."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        cache_key = "trending_posts"
        cached = cache.get(cache_key)

        if cached is not None:
            return cached

        queryset = Post.objects.annotate(
            engagement_score=Count('likes') + Count('comments') * 2
        ).order_by('-engagement_score', '-created_at')[:50]

        cache.set(cache_key, queryset, 300)  # Cache for 5 minutes
        return queryset


class TagPostsView(generics.ListAPIView):
    """Get posts by tag."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        tag_name = self.kwargs.get('tag_name')
        return Post.objects.filter(
            tags__name__iexact=tag_name
        ).select_related('author')
