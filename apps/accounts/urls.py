"""
URL patterns for accounts app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.UserRegisterView.as_view(), name='register'),

    # Profile
    path('me/', views.UserProfileView.as_view(), name='profile'),
    path('<str:username>/', views.UserDetailView.as_view(), name='user-detail'),

    # Search
    path('search/', views.UserSearchView.as_view(), name='user-search'),

    # Follow
    path('<str:username>/follow/', views.follow_user, name='follow-user'),
    path('<str:username>/followers/', views.followers_list, name='followers'),
    path('<str:username>/following/', views.following_list, name='following'),

    # Suggestions
    path('suggested/', views.suggested_users, name='suggested-users'),
]
