from rest_framework import serializers
from .models import Story, StoryView
from apps.accounts.serializers import UserSerializer


class StorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    has_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            'id', 'user', 'story_type', 'media_url', 'caption',
            'background_color', 'text_color', 'views_count',
            'has_viewed', 'created_at', 'expires_at'
        ]
        read_only_fields = ['user', 'views_count', 'created_at']

    def get_has_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoryView.objects.filter(
                story=obj, viewer=request.user
            ).exists()
        return False


class StoryViewSerializer(serializers.ModelSerializer):
    viewer = UserSerializer(read_only=True)

    class Meta:
        model = StoryView
        fields = ['viewer', 'viewed_at']
