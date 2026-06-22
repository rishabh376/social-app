"""
Serializers for posts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, SavedPost, Tag
from apps.accounts.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'posts_count']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent', 'content', 
                  'likes_count', 'replies_count', 'is_liked', 'created_at']
        read_only_fields = ['post', 'author', 'likes_count']

    def get_replies_count(self, obj):
        return obj.replies.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user, comment=obj
            ).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'post_type', 'media_files',
            'location', 'likes_count', 'comments_count', 'shares_count',
            'saves_count', 'is_liked', 'is_saved', 'is_pinned', 'tags',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'author', 'likes_count', 'comments_count', 
            'shares_count', 'saves_count'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user, post=obj
            ).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedPost.objects.filter(
                user=request.user, post=obj
            ).exists()
        return False

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""
    tags_list = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = ['content', 'post_type', 'media_files', 'location', 'tags_list']

    def create(self, validated_data):
        tags_list = validated_data.pop('tags_list', [])
        post = Post.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        # Process tags
        for tag_name in tags_list:
            tag_name = tag_name.lower().strip('#')
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag.posts_count += 1
            tag.save()

        # Update user posts count
        post.author.posts_count = Post.objects.filter(author=post.author).count()
        post.author.save(update_fields=['posts_count'])

        return post
