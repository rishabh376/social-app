"""
Posts, Comments, and Likes models for the social app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    """User post with images/videos."""
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('carousel', 'Carousel'),
    ]

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    content = models.TextField(max_length=2200, blank=True)
    post_type = models.CharField(
        max_length=10, choices=POST_TYPES, default='text'
    )
    media_files = models.JSONField(default=list, blank=True)  # URLs to media
    location = models.CharField(max_length=200, blank=True)

    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    saves_count = models.PositiveIntegerField(default=0)

    # Visibility
    is_archived = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-likes_count']),
        ]

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    """Comment on a post."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies'
    )
    content = models.TextField(max_length=1000)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username}"


class Like(models.Model):
    """Like on a post or comment."""
    LIKE_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes'
    )
    like_type = models.CharField(max_length=10, choices=LIKE_TYPES)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True,
        related_name='likes'
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'
        unique_together = [
            ['user', 'post'],
            ['user', 'comment'],
        ]
        indexes = [
            models.Index(fields=['user', 'like_type']),
        ]

    def __str__(self):
        return f"Like by {self.user.username}"


class SavedPost(models.Model):
    """Saved/bookmarked posts."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='saved_posts'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='saves'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_posts'
        unique_together = ['user', 'post']

    def __str__(self):
        return f"{self.user.username} saved {self.post.id}"


class Tag(models.Model):
    """Hashtag for posts."""
    name = models.CharField(max_length=100, unique=True)
    posts_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return f"#{self.name}"


class PostTag(models.Model):
    """Many-to-many relationship between posts and tags."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = 'post_tags'
        unique_together = ['post', 'tag']
