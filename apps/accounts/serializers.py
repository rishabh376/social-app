"""
Serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'bio', 'avatar', 'cover_photo', 'phone',
            'is_verified', 'is_online', 'last_seen', 'is_private',
            'followers_count', 'following_count', 'posts_count',
            'is_following', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'is_verified']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user, following=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 
                  'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'avatar', 
                  'cover_photo', 'phone', 'is_private']


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships."""
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['created_at']
