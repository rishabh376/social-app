"""
URL patterns for posts app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Feed
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('trending/', views.TrendingPostsView.as_view(), name='trending'),

    # Posts
    path('', views.PostListCreateView.as_view(), name='posts-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/like/', views.like_post, name='like-post'),
    path('<int:post_id>/save/', views.save_post, name='save-post'),

    # Comments
    path('<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comments'),
    path('comments/<int:comment_id>/like/', views.like_comment, name='like-comment'),

    # Tags
    path('tag/<str:tag_name>/', views.TagPostsView.as_view(), name='tag-posts'),
]
